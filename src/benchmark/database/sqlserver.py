import pyodbc
import os
import uuid
from decimal import Decimal
from datetime import datetime


SQLSERVER_SAMPLES= ('ztb_probka_pac', 'ztb_probka_obs', 'ztb_kopia_obs', 'ztb_kopia_ct','ztb_kopia_pac', 'ztb_kopia_alg', 'ztb_wzorzec','ztb_kopia_z2_claims','ztb_kopia_z2_enc','ztb_kopia_z3_cond', 'ztb_kopia_z3_proc', 'ztb_kopia_z3_obs','ztb_kopia_z4_pat', 
    'ztb_kopia_z4_enc', 'ztb_kopia_z4_alg','ztb_kopia_z4_cond', 'ztb_kopia_z4_obs', 'ztb_kopia_z4_proc','ztb_kopia_z4_med', 'ztb_kopia_z4_claims', 'ztb_kopia_z4_ct'
)

SQLSERVER_IDXS= (('ENCOUNTERS','PatientId'), ('ALLERGIES','PatientId'), ('ALLERGIES','EncounterId'),('CONDITIONS','PatientId'), ('CONDITIONS','EncounterId'),('OBSERVATIONS','PatientId'), ('OBSERVATIONS','EncounterId'), ('OBSERVATIONS','Code'),('PROCEDURES','PatientId'), ('PROCEDURES','EncounterId'),
    ('MEDICATIONS','PatientId'), ('MEDICATIONS','EncounterId'),('CLAIMS','PatientId'), ('CLAIMS','EncounterId'),('CLAIMS_TRANSACTIONS','ClaimId'), ('CLAIMS_TRANSACTIONS','PatientId'),('CLAIMS_TRANSACTIONS','EncounterId')
)


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


def prepare_samples():
    conn_str=os.environ["SQLSERVER_CONNECTION"]
    with pyodbc.connect(conn_str,autocommit=False) as conn:
        cur=conn.cursor()
        try:
            cur.execute("SET XACT_ABORT ON")
            for name in SQLSERVER_SAMPLES: cur.execute(f"DROP TABLE IF EXISTS dbo.[{name}]")

            cur.execute("SELECT COUNT_BIG(*) FROM dbo.[PATIENTS]")
            cur_resp=cur.fetchone()
            if cur_resp is None: raise ValueError("No value returend")
            resp_nbm=(cur_resp[0]+9)//10

            cur.execute("""SELECT TOP (?) CAST(ROW_NUMBER() OVER (ORDER BY CONVERT(char(36),[PatientId]) COLLATE Latin1_General_100_BIN2) AS int) AS nr, [PatientId] INTO dbo.[ztb_probka_pac] FROM dbo.[PATIENTS] ORDER BY CONVERT(char(36),[PatientId]) COLLATE Latin1_General_100_BIN2""",resp_nbm)
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_probka_pac_nr] ON dbo.[ztb_probka_pac] ([nr])""")
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_probka_pac_id] ON dbo.[ztb_probka_pac] ([PatientId])""")
            cur.execute("""SELECT TOP (1000) CAST(ROW_NUMBER() OVER (ORDER BY CONVERT(char(36),[ObservationId]) COLLATE Latin1_General_100_BIN2) AS int) AS nr, [ObservationId] INTO dbo.[ztb_probka_obs] FROM dbo.[OBSERVATIONS] WHERE [Type]='numeric' ORDER BY CONVERT(char(36),[ObservationId]) COLLATE Latin1_General_100_BIN2""")
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_probka_obs_nr] ON dbo.[ztb_probka_obs] ([nr])""")
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_probka_obs_id] ON dbo.[ztb_probka_obs] ([ObservationId])""")
            cur.execute("""SELECT o.* INTO dbo.[ztb_kopia_obs] FROM dbo.[OBSERVATIONS] o JOIN dbo.[ztb_probka_obs] p ON p.[ObservationId]=o.[ObservationId]""")
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_kopia_obs_id] ON dbo.[ztb_kopia_obs] ([ObservationId])""")
            cur.execute("""SELECT ct.* INTO dbo.[ztb_kopia_ct] FROM dbo.[CLAIMS_TRANSACTIONS] ct JOIN dbo.[ztb_probka_pac] p ON p.[PatientId]=ct.[PatientId]""")
            cur.execute("""CREATE UNIQUE INDEX [IX_ztb_kopia_ct_id] ON dbo.[ztb_kopia_ct] ([ClaimTransactionId])""")
            cur.execute("""SELECT pa.* INTO dbo.[ztb_kopia_pac] FROM dbo.[PATIENTS] pa JOIN dbo.[ztb_probka_pac] p ON p.[PatientId]=pa.[PatientId] WHERE p.nr=1""")
            cur.execute("""SELECT TOP (1) * INTO dbo.[ztb_kopia_alg] FROM dbo.[ALLERGIES] ORDER BY CONVERT(char(36),[AllergiesId]) COLLATE Latin1_General_100_BIN2""")
            cur.execute("""SELECT TOP (1) e.[OrganizationId],e.[ProviderId],e.[PayerId] INTO dbo.[ztb_wzorzec] FROM dbo.[ENCOUNTERS] e JOIN dbo.[ztb_probka_pac] p ON p.[PatientId]=e.[PatientId] WHERE p.nr=1 ORDER BY CONVERT(char(36),e.[EncounterId]) COLLATE Latin1_General_100_BIN2""")

            sql_cond_copie= (('ztb_kopia_z2_claims','CLAIMS','p.nr<=10'),('ztb_kopia_z2_enc','ENCOUNTERS','p.nr<=10'),('ztb_kopia_z3_cond','CONDITIONS','p.nr<=10 AND t.[EndDate] IS NULL'),('ztb_kopia_z3_proc','PROCEDURES',"p.nr<=10 AND t.[Code]='430193006'"),
                ('ztb_kopia_z3_obs','OBSERVATIONS',"p.nr<=10 AND t.[Code]='8302-2'"),('ztb_kopia_z4_pat','PATIENTS','p.nr=1'),('ztb_kopia_z4_enc','ENCOUNTERS','p.nr=1'),('ztb_kopia_z4_alg','ALLERGIES','p.nr=1'),
                ('ztb_kopia_z4_cond','CONDITIONS','p.nr=1'),('ztb_kopia_z4_obs','OBSERVATIONS','p.nr=1'),('ztb_kopia_z4_proc','PROCEDURES','p.nr=1'),('ztb_kopia_z4_med','MEDICATIONS','p.nr=1'),
                ('ztb_kopia_z4_claims','CLAIMS','p.nr=1'),('ztb_kopia_z4_ct','CLAIMS_TRANSACTIONS','p.nr=1')
            )

            for dest,table,sql_conds in sql_cond_copie:
                cur.execute(f"""SELECT t.* INTO dbo.[{dest}] FROM dbo.[{table}] t JOIN dbo.[ztb_probka_pac] p ON p.[PatientId]=t.[PatientId] WHERE {sql_conds}""")

            cur.execute("SELECT COUNT_BIG(*) FROM dbo.[ztb_probka_pac]")
            npac_resp=cur.fetchone()
            if npac_resp is None: raise ValueError("No returned value")
            n_pac=npac_resp[0]
            cur.execute("SELECT COUNT_BIG(*) FROM dbo.[ztb_probka_obs]")
            nobs_resp=cur.fetchone()
            if nobs_resp is None: raise ValueError("No returned value")  
            n_obs=nobs_resp[0]
            cur.execute("SELECT COUNT_BIG(*) FROM dbo.[ztb_kopia_ct]")
            nct_resp=cur.fetchone()
            if nct_resp is None: raise ValueError("No returned value")
            n_ct=nct_resp[0]
            conn.commit()
            return {"probka_pac":n_pac,"probka_obs":n_obs,"kopia_ct":n_ct}

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()