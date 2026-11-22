import pyodbc
import os
import uuid
from decimal import Decimal
from datetime import datetime


def fix_observation(observation_id:str , next_val: str):
    conn_str=os.environ["SQLSERVER_CONNECTION"]
    with pyodbc.connect(conn_str, autocommit=False) as conn:
        cur=conn.cursor()
        try:
            cur.execute("""UPDATE dbo.[OBSERVATIONS] SET Value= ? WHERE ObservationId= ? """,next_val,observation_id)
            if cur.rowcount!=1: raise ValueError("Uncorrect numer of rows changed")
            cur.execute("""SELECT Value FROM dbo.[OBSERVATIONS] WHERE ObservationId= ? """, observation_id)
            resp=cur.fetchone()
            conn.commit()

            return resp[0]
        except Exception: 
            conn.rollback()
            raise
        finally:
            cur.close()


def remove_medication(withdrawn_code: str,n_code: str,n_descr: str,n_base_cost: float,eff_date: str,)->int:
    if withdrawn_code==n_code: raise ValueError("Withdrawn code is the same as the new one")
    effective_date =datetime.fromisoformat(eff_date)
    base_cost= Decimal(str(n_base_cost))
    if base_cost< 0: raise ValueError("Base count cant be negative")

    conn_str = os.environ["SQLSERVER_CONNECTION"]
    with pyodbc.connect(conn_str,autocommit=False) as conn:
        cur =conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("""SELECT MedicationId, PatientId,EncounterId,PayerId, ReasonCode, ReasonDescription FROM dbo.[MEDICATIONS] WITH (UPDLOCK, HOLDLOCK) WHERE Code= ? AND StartDate <= ? AND (EndDate IS NULL OR EndDate > ?)""",withdrawn_code,effective_date,effective_date)
            affected= cur.fetchall()
            if not affected: raise ValueError("No active medications found")
            for medication in affected:
                cur.execute("""UPDATE dbo.[MEDICATIONS] SET EndDate = ? WHERE MedicationId = ? """,effective_date,medication.MedicationId)
                if cur.rowcount!= 1: raise ValueError("One updated expected")
                new_id= str(uuid.uuid5(uuid.NAMESPACE_URL,f"{medication.MedicationId}:{n_code}:{eff_date}"))
                cur.execute("""INSERT INTO dbo.[MEDICATIONS] (MedicationId,PatientId,EncounterId,PayerId,StartDate,EndDate,Code,Description,Base_Cost,Payer_Coverage,Dispenses,TotalCost,ReasonCode,ReasonDescription)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",new_id,medication.PatientId,medication.EncounterId,medication.PayerId,effective_date,None,n_code,n_descr,base_cost,Decimal("0"),1,base_cost,medication.ReasonCode,medication.ReasonDescription)
                if cur.rowcount != 1: raise ValueError("One inserted expected")
            conn.commit()
            return len(affected)

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()


def register_patient_death(patient_id: str,died_date: str)->int:
    died_dt=datetime.fromisoformat(died_date)
    conn_str= os.environ["SQLSERVER_CONNECTION"]

    with pyodbc.connect(conn_str, autocommit=False) as conn:
        cur=conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("""SELECT DeathDate FROM dbo.[PATIENTS] WITH (UPDLOCK, HOLDLOCK) WHERE PatientId = ? """,patient_id)
            patient= cur.fetchone()
            if patient is None: raise ValueError("No patient")
            if patient.DeathDate is not None: raise ValueError("Patient already DEAD")
            cur.execute("""UPDATE dbo.[PATIENTS] SET DeathDate = ? WHERE PatientId = ? """,died_dt,patient_id)
            if cur.rowcount!=1: raise ValueError("Expected one updated patient")

            cur.execute("""UPDATE dbo.[MEDICATIONS] SET EndDate = ? WHERE PatientId = ? AND StartDate <= ?  AND (EndDate IS NULL OR EndDate > ?)""",died_dt,patient_id,died_dt,died_dt)
            medications_closed= cur.rowcount
            conn.commit()
            return medications_closed

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()


def register_new_allergy(patient_id: str,encounter_id:str, a_code:str, a_descr:str, a_eff_date:str, a_codes: list[str], a_system:str="Unknown")->int:
    a_eff_dt=datetime.fromisoformat(a_eff_date)
    conn_str= os.environ["SQLSERVER_CONNECTION"]

    with pyodbc.connect(conn_str, autocommit=False) as conn:
        cur=conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("SET XACT_ABORT ON")
            cur.execute("""SELECT PatientId FROM dbo.[PATIENTS] WITH (UPDLOCK, HOLDLOCK) WHERE PatientId = ? """,patient_id)
            patient= cur.fetchone()
            if patient is None: raise ValueError("No patient")
            cur.execute("""SELECT EncounterId, PatientId FROM dbo.[ENCOUNTERS] WITH (UPDLOCK, HOLDLOCK) WHERE EncounterId = ? """,encounter_id)
            encounter= cur.fetchone()
            if encounter is None: raise ValueError("No registered encounter")
            if str(encounter.PatientId).lower()!=patient_id.lower(): raise ValueError("Encounter is aligned to another patient")

            cur.execute("""SELECT AllergiesId FROM dbo.[ALLERGIES] WHERE PatientId = ? AND Code = ? AND StartDate <= ? AND (EndDate IS NULL OR EndDate > ?) """,patient_id,a_code,a_eff_dt,a_eff_dt)
            existing=cur.fetchone()
            if existing is not None: raise ValueError("Allergy already registered")
            new_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"{patient_id}:{encounter_id}:{a_code}:{a_eff_date}"))
            cur.execute("""INSERT INTO dbo.[ALLERGIES] (AllergiesId,PatientId,EncounterId,StartDate,Code,[System],Description)
                VALUES (?, ?, ?, ?, ?, ?, ?) """,new_id,patient_id,encounter_id,a_eff_dt,a_code,a_system,a_descr)

            if cur.rowcount!=1: raise ValueError("Expected one inserted allergy")
            medications_closed=0
            if a_codes:
                placeholders=", ".join("?" for _ in a_codes)
                cur.execute(f"""UPDATE dbo.[MEDICATIONS] SET EndDate = ? WHERE PatientId = ? AND StartDate <= ? AND (EndDate IS NULL OR EndDate > ?)
                    AND Code IN ({placeholders}) """,a_eff_dt,patient_id,a_eff_dt,a_eff_dt,*a_codes)
                medications_closed=cur.rowcount

            conn.commit()
            return medications_closed

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
