import psycopg2
import os
import uuid
from decimal import Decimal
from datetime import datetime
from contextlib import closing


def fix_observation(observation_id:str , next_val: str):
    conn_str=os.environ["POSTGRES_CONNECTION"]
    with closing(psycopg2.connect(conn_str)) as conn:
        cur=conn.cursor()
        try:
            cur.execute("""UPDATE public."OBSERVATIONS" SET "Value"= %s WHERE "ObservationId"= %s """,(next_val,observation_id))
            if cur.rowcount!=1: raise ValueError("Uncorrect numer of rows changed")
            cur.execute("""SELECT "Value" FROM public."OBSERVATIONS" WHERE "ObservationId"= %s """, (observation_id,))
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

    conn_str = os.environ["POSTGRES_CONNECTION"]
    with closing(psycopg2.connect(conn_str)) as conn:
        cur =conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("""SELECT "MedicationId", "PatientId","EncounterId","PayerId", "ReasonCode", "ReasonDescription" FROM public."MEDICATIONS" WHERE "Code"= %s AND "StartDate" <= %s AND ("EndDate" IS NULL OR "EndDate" > %s) FOR UPDATE""",(withdrawn_code,effective_date,effective_date))
            affected= cur.fetchall()
            if not affected: raise ValueError("No active medications found")
            for medication in affected:
                cur.execute("""UPDATE public."MEDICATIONS" SET "EndDate" = %s WHERE "MedicationId" = %s """,(effective_date,medication[0]))
                if cur.rowcount!= 1: raise ValueError("One updated expected")
                new_id= str(uuid.uuid5(uuid.NAMESPACE_URL,f"{medication[0]}:{n_code}:{eff_date}"))
                cur.execute("""INSERT INTO public."MEDICATIONS" ("MedicationId","PatientId","EncounterId","PayerId","StartDate","EndDate","Code","Description","Base_Cost","Payer_Coverage","Dispenses","TotalCost","ReasonCode","ReasonDescription")
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(new_id,medication[1],medication[2],medication[3],effective_date,None,n_code,n_descr,base_cost,Decimal("0"),1,base_cost,medication[4],medication[5]))
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
    conn_str= os.environ["POSTGRES_CONNECTION"]

    with closing(psycopg2.connect(conn_str)) as conn:
        cur=conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("""SELECT "DeathDate" FROM public."PATIENTS" WHERE "PatientId" = %s FOR UPDATE """,(patient_id,))
            patient= cur.fetchone()
            if patient is None: raise ValueError("No patient")
            if patient[0] is not None: raise ValueError("Patient already DEAD")
            cur.execute("""UPDATE public."PATIENTS" SET "DeathDate" = %s WHERE "PatientId" = %s """,(died_dt,patient_id))
            if cur.rowcount!=1: raise ValueError("Expected one updated patient")

            cur.execute("""UPDATE public."MEDICATIONS" SET "EndDate" = %s WHERE "PatientId" = %s AND "StartDate" <= %s  AND ("EndDate" IS NULL OR "EndDate" > %s)""",(died_dt,patient_id,died_dt,died_dt))
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
    conn_str= os.environ["POSTGRES_CONNECTION"]

    with closing(psycopg2.connect(conn_str)) as conn:
        cur=conn.cursor()
        try:
            cur.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            cur.execute("""SELECT "PatientId" FROM public."PATIENTS" WHERE "PatientId" = %s FOR UPDATE """,(patient_id,))
            patient= cur.fetchone()
            if patient is None: raise ValueError("No patient")
            cur.execute("""SELECT "EncounterId", "PatientId" FROM public."ENCOUNTERS" WHERE "EncounterId" = %s FOR UPDATE """,(encounter_id,))
            encounter= cur.fetchone()
            if encounter is None: raise ValueError("No registered encounter")
            if str(encounter[1]).lower()!=patient_id.lower(): raise ValueError("Encounter is aligned to another patient")

            cur.execute("""SELECT "AllergiesId" FROM public."ALLERGIES" WHERE "PatientId" = %s AND "Code" = %s AND "StartDate" <= %s AND ("EndDate" IS NULL OR "EndDate" > %s) """,(patient_id,a_code,a_eff_dt,a_eff_dt))
            existing=cur.fetchone()
            if existing is not None: raise ValueError("Allergy already registered")
            new_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"{patient_id}:{encounter_id}:{a_code}:{a_eff_date}"))
            cur.execute("""INSERT INTO public."ALLERGIES" ("AllergiesId","PatientId","EncounterId","StartDate","Code","System","Description")
                VALUES (%s, %s, %s, %s, %s, %s, %s) """,(new_id,patient_id,encounter_id,a_eff_dt,a_code,a_system,a_descr))
            if cur.rowcount!=1: raise ValueError("Expected one inserted allergy")

            medications_closed=0
            if a_codes:
                cur.execute("""UPDATE public."MEDICATIONS" SET "EndDate" = %s WHERE "PatientId" = %s AND "StartDate" <= %s AND ("EndDate" IS NULL OR "EndDate" > %s)
                    AND "Code" = ANY(%s) """,(a_eff_dt,patient_id,a_eff_dt,a_eff_dt,list(a_codes)))
                medications_closed=cur.rowcount

            conn.commit()
            return medications_closed

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
