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
            resp=cur.all()
            conn.commit()

            return resp[0]
        except Exception: 
            conn.rollback()
            raise
        finally:
            cur.close()


def withdrawn_medication(withdrawn_code: str,n_code: str,n_descr: str,n_base_cost: float,eff_date: str,)->int:
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
                cur.execute("""INSERT INTO dbo.[MEDICATIONS] (MedicationId,PatientId,EncounterId,PayerId,StartDate,EndDate,Code,Description,BaseCost,PayerCoverage,Dispenses,TotalCost,ReasonCode,ReasonDescription)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",new_id,medication.PatientId,medication.EncounterId,medication.PayerId,effective_date,None,n_code,n_descr,base_cost,Decimal("0"),1,base_cost,medication.ReasonCode,medication.ReasonDescription)
                if cur.rowcount != 1: raise ValueError("One inserted expected")
            conn.commit()
            return len(affected)

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
