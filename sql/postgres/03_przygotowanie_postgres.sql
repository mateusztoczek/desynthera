DROP TABLE IF EXISTS ztb_probka_pac, ztb_probka_obs, ztb_kopia_obs, ztb_kopia_ct,
    ztb_kopia_pac, ztb_kopia_alg, ztb_wzorzec,
    ztb_kopia_z2_claims, ztb_kopia_z2_enc, ztb_kopia_z3_cond, ztb_kopia_z3_proc, ztb_kopia_z3_obs,
    ztb_kopia_z4_pat, ztb_kopia_z4_enc, ztb_kopia_z4_alg, ztb_kopia_z4_cond, ztb_kopia_z4_obs,
    ztb_kopia_z4_proc, ztb_kopia_z4_med, ztb_kopia_z4_claims, ztb_kopia_z4_ct;

CREATE TABLE ztb_probka_pac AS
SELECT row_number() OVER (ORDER BY "PatientId"::text COLLATE "C")::int AS nr, "PatientId"
FROM public."PATIENTS"
ORDER BY "PatientId"::text COLLATE "C"
LIMIT (SELECT ceil(count(*)*0.10)::bigint FROM public."PATIENTS");
CREATE UNIQUE INDEX ON ztb_probka_pac (nr);
CREATE UNIQUE INDEX ON ztb_probka_pac ("PatientId");

CREATE TABLE ztb_probka_obs AS
SELECT row_number() OVER (ORDER BY "ObservationId"::text COLLATE "C")::int AS nr, "ObservationId"
FROM public."OBSERVATIONS"
WHERE "Type" = 'numeric'
ORDER BY "ObservationId"::text COLLATE "C"
LIMIT 1000;
CREATE UNIQUE INDEX ON ztb_probka_obs (nr);
CREATE UNIQUE INDEX ON ztb_probka_obs ("ObservationId");

CREATE TABLE ztb_kopia_obs AS
SELECT o.* FROM public."OBSERVATIONS" o JOIN ztb_probka_obs p ON p."ObservationId" = o."ObservationId";
CREATE UNIQUE INDEX ON ztb_kopia_obs ("ObservationId");

CREATE TABLE ztb_kopia_ct AS
SELECT ct.* FROM public."CLAIMS_TRANSACTIONS" ct JOIN ztb_probka_pac p ON p."PatientId" = ct."PatientId";
CREATE UNIQUE INDEX ON ztb_kopia_ct ("ClaimTransactionId");

CREATE TABLE ztb_kopia_pac AS
SELECT pa.* FROM public."PATIENTS" pa JOIN ztb_probka_pac p ON p."PatientId" = pa."PatientId" WHERE p.nr = 1;

CREATE TABLE ztb_kopia_alg AS
SELECT * FROM public."ALLERGIES" ORDER BY "AllergiesId"::text COLLATE "C" LIMIT 1;

CREATE TABLE ztb_wzorzec AS
SELECT e."OrganizationId", e."ProviderId", e."PayerId"
FROM public."ENCOUNTERS" e JOIN ztb_probka_pac p ON p."PatientId" = e."PatientId"
WHERE p.nr = 1
ORDER BY e."EncounterId"::text COLLATE "C"
LIMIT 1;

CREATE TABLE ztb_kopia_z2_claims AS
SELECT c.* FROM public."CLAIMS" c JOIN ztb_probka_pac p ON p."PatientId" = c."PatientId" WHERE p.nr <= 10;
CREATE TABLE ztb_kopia_z2_enc AS
SELECT e.* FROM public."ENCOUNTERS" e JOIN ztb_probka_pac p ON p."PatientId" = e."PatientId" WHERE p.nr <= 10;

CREATE TABLE ztb_kopia_z3_cond AS
SELECT c.* FROM public."CONDITIONS" c JOIN ztb_probka_pac p ON p."PatientId" = c."PatientId"
WHERE p.nr <= 10 AND c."EndDate" IS NULL;
CREATE TABLE ztb_kopia_z3_proc AS
SELECT pr.* FROM public."PROCEDURES" pr JOIN ztb_probka_pac p ON p."PatientId" = pr."PatientId"
WHERE p.nr <= 10 AND pr."Code" = '430193006';
CREATE TABLE ztb_kopia_z3_obs AS
SELECT o.* FROM public."OBSERVATIONS" o JOIN ztb_probka_pac p ON p."PatientId" = o."PatientId"
WHERE p.nr <= 10 AND o."Code" = '8302-2';

CREATE TABLE ztb_kopia_z4_pat    AS SELECT t.* FROM public."PATIENTS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_enc    AS SELECT t.* FROM public."ENCOUNTERS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_alg    AS SELECT t.* FROM public."ALLERGIES" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_cond   AS SELECT t.* FROM public."CONDITIONS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_obs    AS SELECT t.* FROM public."OBSERVATIONS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_proc   AS SELECT t.* FROM public."PROCEDURES" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_med    AS SELECT t.* FROM public."MEDICATIONS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_claims AS SELECT t.* FROM public."CLAIMS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;
CREATE TABLE ztb_kopia_z4_ct     AS SELECT t.* FROM public."CLAIMS_TRANSACTIONS" t JOIN ztb_probka_pac p ON p."PatientId" = t."PatientId" WHERE p.nr = 1;

ANALYZE;

SELECT 'probka_pac' AS obiekt, count(*) FROM ztb_probka_pac
UNION ALL SELECT 'probka_obs', count(*) FROM ztb_probka_obs
UNION ALL SELECT 'kopia_ct (10% CT)', count(*) FROM ztb_kopia_ct
UNION ALL SELECT 'z2_claims', count(*) FROM ztb_kopia_z2_claims
UNION ALL SELECT 'z3_cond', count(*) FROM ztb_kopia_z3_cond
UNION ALL SELECT 'z3_proc', count(*) FROM ztb_kopia_z3_proc
UNION ALL SELECT 'z3_obs', count(*) FROM ztb_kopia_z3_obs
UNION ALL SELECT 'z4_obs', count(*) FROM ztb_kopia_z4_obs
UNION ALL SELECT 'z4_ct', count(*) FROM ztb_kopia_z4_ct;
