-- @@ C1
INSERT INTO public."PATIENTS" ("PatientId","BirthDate","DeathDate","SSN","FirstName","LastName",
    "Suffix","MaritalStatus","Race","Gender","Address","City")
VALUES ('00000000-0000-4000-8000-000000000001', DATE '1990-01-01', NULL, '999-00-0001',
        'Jan', 'Testowy', NULL, 'S', 'white', 'M', 'ul. Testowa 1', 'Krakow');

-- @@ C1 przywrocenie
DELETE FROM public."PATIENTS" WHERE "PatientId" = '00000000-0000-4000-8000-000000000001';

-- @@ C2
DO $$
DECLARE i int;
BEGIN
  FOR i IN 1..1000 LOOP
    INSERT INTO public."OBSERVATIONS" ("PatientId","EncounterId","ObservationDate","Category",
        "Code","Description","Value","Units","Type")
    SELECT k."PatientId", k."EncounterId", TIMESTAMP '2099-01-01', k."Category",
           k."Code", k."Description", k."Value", k."Units", k."Type"
    FROM ztb_kopia_obs k JOIN ztb_probka_obs p ON p."ObservationId" = k."ObservationId"
    WHERE p.nr = i;
    COMMIT;
  END LOOP;
END $$;

-- @@ C2 przywrocenie
DELETE FROM public."OBSERVATIONS" WHERE "ObservationDate" = TIMESTAMP '2099-01-01';

-- @@ C3
DO $$
DECLARE b int;
BEGIN
  FOR b IN 0..9 LOOP
    INSERT INTO public."OBSERVATIONS" ("PatientId","EncounterId","ObservationDate","Category",
        "Code","Description","Value","Units","Type")
    SELECT k."PatientId", k."EncounterId", TIMESTAMP '2099-01-01', k."Category",
           k."Code", k."Description", k."Value", k."Units", k."Type"
    FROM ztb_kopia_obs k JOIN ztb_probka_obs p ON p."ObservationId" = k."ObservationId"
    WHERE p.nr BETWEEN b * 100 + 1 AND b * 100 + 100;
    COMMIT;
  END LOOP;
END $$;

-- @@ C3 przywrocenie
DELETE FROM public."OBSERVATIONS" WHERE "ObservationDate" = TIMESTAMP '2099-01-01';

-- @@ C4
INSERT INTO public."OBSERVATIONS" ("PatientId","EncounterId","ObservationDate","Category",
    "Code","Description","Value","Units","Type")
SELECT k."PatientId", k."EncounterId", TIMESTAMP '2099-01-01', k."Category",
       k."Code", k."Description", k."Value", k."Units", k."Type"
FROM ztb_kopia_obs k;

-- @@ C4 przywrocenie
DELETE FROM public."OBSERVATIONS" WHERE "ObservationDate" = TIMESTAMP '2099-01-01';

-- @@ C5
INSERT INTO public."CLAIMS_TRANSACTIONS" ("ClaimTransactionId","ClaimId","PatientId","EncounterId",
    "OrganizationId","ProviderId","ChargeId","TransactionType","Amount","Method","FromDate","ToDate",
    "ProcedureCode","Units","UnitAmount","DiagnosisRef1","DiagnosisRef2","DiagnosisRef3","DiagnosisRef4",
    "Payments","Adjustments","Transfers","Outstanding","TransferOutId","TransferType","Notes","LineNote")
SELECT gen_random_uuid(), k."ClaimId", k."PatientId", k."EncounterId",
       k."OrganizationId", k."ProviderId", k."ChargeId", k."TransactionType", k."Amount", k."Method",
       TIMESTAMP '2099-01-01', k."ToDate",
       k."ProcedureCode", k."Units", k."UnitAmount", k."DiagnosisRef1", k."DiagnosisRef2", k."DiagnosisRef3", k."DiagnosisRef4",
       k."Payments", k."Adjustments", k."Transfers", k."Outstanding", k."TransferOutId", k."TransferType", k."Notes", k."LineNote"
FROM ztb_kopia_ct k;

-- @@ C5 przywrocenie
DELETE FROM public."CLAIMS_TRANSACTIONS" WHERE "FromDate" = TIMESTAMP '2099-01-01';

-- @@ C6
DO $$
DECLARE i int;
BEGIN
  FOR i IN 1..1000 LOOP
    INSERT INTO public."OBSERVATIONS" ("PatientId","EncounterId","ObservationDate","Category",
        "Code","Description","Value","Units","Type")
    SELECT k."PatientId", k."EncounterId", TIMESTAMP '2099-01-01', k."Category",
           k."Code", k."Description", k."Value", k."Units", k."Type"
    FROM ztb_kopia_obs k JOIN ztb_probka_obs p ON p."ObservationId" = k."ObservationId"
    WHERE p.nr = i;
  END LOOP;
END $$;

-- @@ C6 przywrocenie
DELETE FROM public."OBSERVATIONS" WHERE "ObservationDate" = TIMESTAMP '2099-01-01';

-- @@ R1
SELECT pa.* FROM public."PATIENTS" pa
WHERE pa."PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);

-- @@ R2
DO $$
DECLARE i int; v text;
BEGIN
  FOR i IN 1..1000 LOOP
    SELECT o."Value" INTO v FROM public."OBSERVATIONS" o
    WHERE o."ObservationId" = (SELECT "ObservationId" FROM ztb_probka_obs WHERE nr = i);
    COMMIT;
  END LOOP;
END $$;

-- @@ R3
DO $$
DECLARE b int; s bigint;
BEGIN
  FOR b IN 0..9 LOOP
    SELECT sum(length(o."Value")) INTO s
    FROM public."OBSERVATIONS" o JOIN ztb_probka_obs p ON p."ObservationId" = o."ObservationId"
    WHERE p.nr BETWEEN b * 100 + 1 AND b * 100 + 100;
    COMMIT;
  END LOOP;
END $$;

-- @@ R4
SELECT o.* FROM public."OBSERVATIONS" o
JOIN ztb_probka_obs p ON p."ObservationId" = o."ObservationId";

-- @@ R5
SELECT ct."TransactionType", count(*) AS liczba, sum(ct."Amount") AS kwota,
       sum(ct."Payments") AS platnosci, sum(ct."Outstanding") AS zaleglosci
FROM public."CLAIMS_TRANSACTIONS" ct
JOIN ztb_probka_pac p ON p."PatientId" = ct."PatientId"
GROUP BY ct."TransactionType"
ORDER BY ct."TransactionType";

-- @@ R6
WITH pac AS (
    SELECT "PatientId" FROM ztb_probka_pac WHERE nr <= 10
), obs AS (
    SELECT o."EncounterId", count(*) AS n FROM public."OBSERVATIONS" o
    WHERE o."PatientId" IN (SELECT "PatientId" FROM pac) GROUP BY o."EncounterId"
), cond AS (
    SELECT c."EncounterId", count(*) AS n FROM public."CONDITIONS" c
    WHERE c."PatientId" IN (SELECT "PatientId" FROM pac) GROUP BY c."EncounterId"
), koszt AS (
    SELECT cl."EncounterId", sum(ct."Amount") AS kwota
    FROM public."CLAIMS" cl JOIN public."CLAIMS_TRANSACTIONS" ct ON ct."ClaimId" = cl."ClaimId"
    WHERE cl."PatientId" IN (SELECT "PatientId" FROM pac) GROUP BY cl."EncounterId"
)
SELECT pa."PatientId", pa."LastName", e."StartDate", e."Description",
       coalesce(obs.n, 0) AS obserwacje, coalesce(cond.n, 0) AS rozpoznania, koszt.kwota
FROM pac
JOIN public."PATIENTS" pa ON pa."PatientId" = pac."PatientId"
JOIN public."ENCOUNTERS" e ON e."PatientId" = pa."PatientId"
LEFT JOIN obs ON obs."EncounterId" = e."EncounterId"
LEFT JOIN cond ON cond."EncounterId" = e."EncounterId"
LEFT JOIN koszt ON koszt."EncounterId" = e."EncounterId"
ORDER BY pa."PatientId", e."StartDate";

-- @@ U1
UPDATE public."PATIENTS"
SET "Address" = "Address" || ' /m. 1'
WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);

-- @@ U1 przywrocenie
UPDATE public."PATIENTS" pa SET "Address" = k."Address"
FROM ztb_kopia_pac k WHERE k."PatientId" = pa."PatientId";

-- @@ U2
DO $$
DECLARE i int;
BEGIN
  FOR i IN 1..1000 LOOP
    UPDATE public."OBSERVATIONS" SET "Value" = "Value" || '1'
    WHERE "ObservationId" = (SELECT "ObservationId" FROM ztb_probka_obs WHERE nr = i);
    COMMIT;
  END LOOP;
END $$;

-- @@ U2 przywrocenie
UPDATE public."OBSERVATIONS" o SET "Value" = k."Value"
FROM ztb_kopia_obs k WHERE k."ObservationId" = o."ObservationId";

-- @@ U3
DO $$
DECLARE b int;
BEGIN
  FOR b IN 0..9 LOOP
    UPDATE public."OBSERVATIONS" o SET "Value" = o."Value" || '1'
    FROM ztb_probka_obs p
    WHERE p."ObservationId" = o."ObservationId" AND p.nr BETWEEN b * 100 + 1 AND b * 100 + 100;
    COMMIT;
  END LOOP;
END $$;

-- @@ U3 przywrocenie
UPDATE public."OBSERVATIONS" o SET "Value" = k."Value"
FROM ztb_kopia_obs k WHERE k."ObservationId" = o."ObservationId";

-- @@ U4
UPDATE public."OBSERVATIONS" o SET "Value" = o."Value" || '1'
FROM ztb_probka_obs p WHERE p."ObservationId" = o."ObservationId";

-- @@ U4 przywrocenie
UPDATE public."OBSERVATIONS" o SET "Value" = k."Value"
FROM ztb_kopia_obs k WHERE k."ObservationId" = o."ObservationId";

-- @@ U5
UPDATE public."CLAIMS_TRANSACTIONS" ct SET "Units" = ct."Units" + 1
FROM ztb_probka_pac p WHERE p."PatientId" = ct."PatientId";

-- @@ U5 przywrocenie
UPDATE public."CLAIMS_TRANSACTIONS" ct SET "Units" = k."Units"
FROM ztb_kopia_ct k WHERE k."ClaimTransactionId" = ct."ClaimTransactionId";

-- @@ U6
UPDATE public."OBSERVATIONS" o SET "Value" = o."Value"
FROM ztb_probka_obs p WHERE p."ObservationId" = o."ObservationId";

-- @@ D1
DELETE FROM public."ALLERGIES" WHERE "AllergiesId" = (SELECT "AllergiesId" FROM ztb_kopia_alg);

-- @@ D1 przywrocenie
INSERT INTO public."ALLERGIES" SELECT * FROM ztb_kopia_alg;

-- @@ D2
DO $$
DECLARE i int;
BEGIN
  FOR i IN 1..1000 LOOP
    DELETE FROM public."OBSERVATIONS"
    WHERE "ObservationId" = (SELECT "ObservationId" FROM ztb_probka_obs WHERE nr = i);
    COMMIT;
  END LOOP;
END $$;

-- @@ D2 przywrocenie
INSERT INTO public."OBSERVATIONS" SELECT * FROM ztb_kopia_obs;

-- @@ D3
DO $$
DECLARE b int;
BEGIN
  FOR b IN 0..9 LOOP
    DELETE FROM public."OBSERVATIONS" o USING ztb_probka_obs p
    WHERE p."ObservationId" = o."ObservationId" AND p.nr BETWEEN b * 100 + 1 AND b * 100 + 100;
    COMMIT;
  END LOOP;
END $$;

-- @@ D3 przywrocenie
INSERT INTO public."OBSERVATIONS" SELECT * FROM ztb_kopia_obs;

-- @@ D4
DELETE FROM public."OBSERVATIONS" o USING ztb_probka_obs p
WHERE p."ObservationId" = o."ObservationId";

-- @@ D4 przywrocenie
INSERT INTO public."OBSERVATIONS" SELECT * FROM ztb_kopia_obs;

-- @@ D5
DELETE FROM public."CLAIMS_TRANSACTIONS" ct USING ztb_probka_pac p
WHERE p."PatientId" = ct."PatientId";

-- @@ D5 przywrocenie
INSERT INTO public."CLAIMS_TRANSACTIONS" SELECT * FROM ztb_kopia_ct;

-- @@ D6
DO $$
DECLARE i int;
BEGIN
  FOR i IN 1..1000 LOOP
    DELETE FROM public."OBSERVATIONS"
    WHERE "ObservationId" = (SELECT "ObservationId" FROM ztb_probka_obs WHERE nr = i);
  END LOOP;
END $$;

-- @@ D6 przywrocenie
INSERT INTO public."OBSERVATIONS" SELECT * FROM ztb_kopia_obs;

-- @@ Z1
BEGIN;
INSERT INTO public."PATIENTS" ("PatientId","BirthDate","DeathDate","SSN","FirstName","LastName",
    "Suffix","MaritalStatus","Race","Gender","Address","City")
VALUES ('00000000-0000-4000-8000-000000000002', DATE '1985-05-05', NULL, '999-00-0002',
        'Anna', 'Przyjeta', NULL, 'M', 'white', 'F', 'ul. Szpitalna 2', 'Krakow');

INSERT INTO public."ENCOUNTERS" ("EncounterId","PatientId","StartDate","EndDate","OrganizationId",
    "ProviderId","PayerId","Code","Description","EncounterClass","Base_Encounter_Cost",
    "Total_Claim_Cost","Payer_Coverage","ReasonCode","ReasonDescription")
SELECT '00000000-0000-4000-8000-000000000102', '00000000-0000-4000-8000-000000000002',
       TIMESTAMP '2099-01-01 08:00', TIMESTAMP '2099-01-01 08:30', w."OrganizationId",
       w."ProviderId", w."PayerId", '185349003', 'Encounter for check up (procedure)', 'ambulatory',
       136.80, 136.80, 0, NULL, NULL
FROM ztb_wzorzec w;

INSERT INTO public."OBSERVATIONS" ("PatientId","EncounterId","ObservationDate","Category",
    "Code","Description","Value","Units","Type")
SELECT '00000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000102',
       TIMESTAMP '2099-01-01 08:10', k."Category", k."Code", k."Description", k."Value", k."Units", k."Type"
FROM ztb_kopia_obs k JOIN ztb_probka_obs p ON p."ObservationId" = k."ObservationId"
WHERE p.nr <= 10;

INSERT INTO public."CONDITIONS" ("PatientId","EncounterId","StartDate","EndDate","System","Code","Description")
VALUES ('00000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000102',
        DATE '2099-01-01', NULL, 'SNOMED-CT', '59621000', 'Essential hypertension (disorder)'),
       ('00000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000102',
        DATE '2099-01-01', NULL, 'SNOMED-CT', '44054006', 'Diabetes mellitus type 2 (disorder)');

INSERT INTO public."PROCEDURES" ("PatientId","EncounterId","StartDate","EndDate","System","Code",
    "Description","Base_Cost","ReasonCode","ReasonDescription")
VALUES ('00000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000102',
        TIMESTAMP '2099-01-01 08:15', TIMESTAMP '2099-01-01 08:20', 'SNOMED-CT', '430193006',
        'Medication reconciliation (procedure)', 463.04, NULL, NULL);

INSERT INTO public."MEDICATIONS" ("PatientId","EncounterId","PayerId","StartDate","EndDate","Code",
    "Description","Base_Cost","Payer_Coverage","Dispenses","TotalCost","ReasonCode","ReasonDescription")
SELECT '00000000-0000-4000-8000-000000000002', '00000000-0000-4000-8000-000000000102', w."PayerId",
       TIMESTAMP '2099-01-01 08:25', NULL, '314076', 'lisinopril 10 MG Oral Tablet',
       12.50, 0, 1, 12.50, '59621000', 'Essential hypertension (disorder)'
FROM ztb_wzorzec w;

INSERT INTO public."CLAIMS" ("ClaimId","PatientId","ProviderId","EncounterId","PrimaryPayerId",
    "SecondaryPayerId","CurrentIllnessDate","ServiceDate","Diagnosis1","Diagnosis2","Status1","StatusP",
    "Outstanding1","OutstandingP","LastBilledDate1","LastBilledDateP")
SELECT '00000000-0000-4000-8000-000000000202', '00000000-0000-4000-8000-000000000002', w."ProviderId",
       '00000000-0000-4000-8000-000000000102', w."PayerId", NULL,
       TIMESTAMP '2099-01-01 08:00', TIMESTAMP '2099-01-01 08:00', '59621000', '44054006',
       'BILLED', 'BILLED', 612.34, 612.34, TIMESTAMP '2099-01-01 08:30', TIMESTAMP '2099-01-01 08:30'
FROM ztb_wzorzec w;

INSERT INTO public."CLAIMS_TRANSACTIONS" ("ClaimTransactionId","ClaimId","PatientId","EncounterId",
    "OrganizationId","ProviderId","ChargeId","TransactionType","Amount","Method","FromDate","ToDate",
    "ProcedureCode","Units","UnitAmount","DiagnosisRef1","Payments","Adjustments","Transfers",
    "Outstanding","Notes")
SELECT gen_random_uuid(), '00000000-0000-4000-8000-000000000202', '00000000-0000-4000-8000-000000000002',
       '00000000-0000-4000-8000-000000000102', w."OrganizationId", w."ProviderId", v.charge,
       'CHARGE', v.kwota, NULL, TIMESTAMP '2099-01-01 08:00', TIMESTAMP '2099-01-01 08:30',
       v.kod, 1, v.kwota, 1, 0, 0, 0, v.kwota, v.opis
FROM ztb_wzorzec w
CROSS JOIN (VALUES (1, 136.80, '185349003', 'Encounter for check up (procedure)'),
                   (2, 463.04, '430193006', 'Medication reconciliation (procedure)'),
                   (3,  12.50, '314076',    'lisinopril 10 MG Oral Tablet')) AS v(charge, kwota, kod, opis);
COMMIT;

-- @@ Z1 przywrocenie
BEGIN;
DELETE FROM public."CLAIMS_TRANSACTIONS" WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."CLAIMS"              WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."MEDICATIONS"         WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."PROCEDURES"          WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."CONDITIONS"          WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."OBSERVATIONS"        WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."ENCOUNTERS"          WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
DELETE FROM public."PATIENTS"            WHERE "PatientId" = '00000000-0000-4000-8000-000000000002';
COMMIT;

-- @@ Z2
BEGIN;
INSERT INTO public."CLAIMS_TRANSACTIONS" ("ClaimTransactionId","ClaimId","PatientId","EncounterId",
    "OrganizationId","ProviderId","ChargeId","TransactionType","Amount","Method","FromDate","ToDate",
    "ProcedureCode","Units","UnitAmount","DiagnosisRef1","Payments","Adjustments","Transfers",
    "Outstanding","Notes")
SELECT gen_random_uuid(), ct."ClaimId", ct."PatientId", ct."EncounterId",
       ct."OrganizationId", ct."ProviderId", ct."ChargeId", 'PAYMENT', NULL, 'ECHECK',
       TIMESTAMP '2099-01-01', TIMESTAMP '2099-01-01',
       ct."ProcedureCode", ct."Units", ct."UnitAmount", ct."DiagnosisRef1", ct."Amount", 0, 0, 0,
       'Z2 doplata'
FROM public."CLAIMS_TRANSACTIONS" ct
JOIN ztb_probka_pac p ON p."PatientId" = ct."PatientId"
WHERE p.nr <= 10 AND ct."TransactionType" = 'CHARGE';

UPDATE public."CLAIMS" c
SET "StatusP" = 'CLOSED', "OutstandingP" = 0, "LastBilledDateP" = TIMESTAMP '2099-01-01'
FROM ztb_probka_pac p
WHERE p."PatientId" = c."PatientId" AND p.nr <= 10;

UPDATE public."ENCOUNTERS" e
SET "Payer_Coverage" = e."Total_Claim_Cost"
FROM ztb_probka_pac p
WHERE p."PatientId" = e."PatientId" AND p.nr <= 10;
COMMIT;

-- @@ Z2 przywrocenie
BEGIN;
DELETE FROM public."CLAIMS_TRANSACTIONS"
WHERE "FromDate" = TIMESTAMP '2099-01-01' AND "Notes" = 'Z2 doplata';
UPDATE public."CLAIMS" c
SET "StatusP" = k."StatusP", "OutstandingP" = k."OutstandingP", "LastBilledDateP" = k."LastBilledDateP"
FROM ztb_kopia_z2_claims k WHERE k."ClaimId" = c."ClaimId";
UPDATE public."ENCOUNTERS" e
SET "Payer_Coverage" = k."Payer_Coverage"
FROM ztb_kopia_z2_enc k WHERE k."EncounterId" = e."EncounterId";
COMMIT;

-- @@ Z3
BEGIN;
UPDATE public."CONDITIONS" c
SET "EndDate" = DATE '2099-01-01'
FROM ztb_probka_pac p
WHERE p."PatientId" = c."PatientId" AND p.nr <= 10 AND c."EndDate" IS NULL;

UPDATE public."OBSERVATIONS" o
SET "Value" = o."Value" || '1'
FROM ztb_probka_pac p
WHERE p."PatientId" = o."PatientId" AND p.nr <= 10 AND o."Code" = '8302-2';

DELETE FROM public."PROCEDURES" pr USING ztb_probka_pac p
WHERE p."PatientId" = pr."PatientId" AND p.nr <= 10 AND pr."Code" = '430193006';
COMMIT;

-- @@ Z3 przywrocenie
BEGIN;
UPDATE public."CONDITIONS" c SET "EndDate" = NULL
FROM ztb_kopia_z3_cond k WHERE k."ConditionId" = c."ConditionId";
UPDATE public."OBSERVATIONS" o SET "Value" = k."Value"
FROM ztb_kopia_z3_obs k WHERE k."ObservationId" = o."ObservationId";
INSERT INTO public."PROCEDURES" SELECT * FROM ztb_kopia_z3_proc;
COMMIT;

-- @@ Z4
BEGIN;
DELETE FROM public."CLAIMS_TRANSACTIONS" WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."CLAIMS"              WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."MEDICATIONS"         WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."PROCEDURES"          WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."OBSERVATIONS"        WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."CONDITIONS"          WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."ALLERGIES"           WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."ENCOUNTERS"          WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
DELETE FROM public."PATIENTS"            WHERE "PatientId" = (SELECT "PatientId" FROM ztb_probka_pac WHERE nr = 1);
COMMIT;

-- @@ Z4 przywrocenie
BEGIN;
INSERT INTO public."PATIENTS"            SELECT * FROM ztb_kopia_z4_pat;
INSERT INTO public."ENCOUNTERS"          SELECT * FROM ztb_kopia_z4_enc;
INSERT INTO public."ALLERGIES"           SELECT * FROM ztb_kopia_z4_alg;
INSERT INTO public."CONDITIONS"          SELECT * FROM ztb_kopia_z4_cond;
INSERT INTO public."OBSERVATIONS"        SELECT * FROM ztb_kopia_z4_obs;
INSERT INTO public."PROCEDURES"          SELECT * FROM ztb_kopia_z4_proc;
INSERT INTO public."MEDICATIONS"         SELECT * FROM ztb_kopia_z4_med;
INSERT INTO public."CLAIMS"              SELECT * FROM ztb_kopia_z4_claims;
INSERT INTO public."CLAIMS_TRANSACTIONS" SELECT * FROM ztb_kopia_z4_ct;
COMMIT;
