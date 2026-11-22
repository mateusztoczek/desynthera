drop table if exists "CLAIMS_TRANSACTIONS";
drop TABLE if EXISTS "CLAIMS";
drop table if exists "MEDICATIONS";
DROP TABLE IF EXISTS "ALLERGIES";
drop table if exists "CONDITIONS";
drop table if exists "OBSERVATIONS";
drop table if exists "PROCEDURES";
DROP TABLE IF EXISTS "ENCOUNTERS";
drop table if exists "PROVIDERS";
drop table if exists "PAYERS";
drop table IF EXISTS "PATIENTS";
drop table IF EXISTS "ORGANIZATIONS";



-- create PATIENTS table with default, common syntax 
create table public."PATIENTS"(
"PatientId" uuid not null PRIMARY KEY,
"BirthDate" date not null,
"DeathDate" date null,
"SSN" varchar(20) null,
"FirstName" varchar(200) not null,
"LastName" varchar(200) not null,
"Suffix" varchar(20) null,
"MaritalStatus" varchar(10) null,
"Race" varchar(30) not null,
"Gender" char(1) not null,
"Address" varchar(300) not null,
"City" varchar(300) not null
);




--create ALLERGIES table with default, common syntax
create table public."ALLERGIES"(
"AllergiesId" uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
"PatientId" uuid not null,
"EncounterId" uuid not null,
"StartDate" date not null,
"EndDate" date null,
"Code" varchar(200) not null,
"System" VARCHAR(50) not null, 
"Description" varchar(500) not null,
"Type" varchar(20) null,
"Category" varchar(20) null,
"Reaction1" varchar(100) null,
"Description1" varchar(200) null,
"Severity1" varchar(20) null,
"Reaction2" varchar(100) null,
"Description2" varchar(200) null,
"Severity2" varchar(20) null,

CONSTRAINT "FK_ALLERGIES_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId")
);


 
--create ENCOUNTERS table with default, common syntax
create table public."ENCOUNTERS"(
"EncounterId" uuid not null primary key,
"PatientId" uuid not null,
"StartDate" timestamp(0) not null,
"EndDate" timestamp(0) NULL,
"OrganizationId" uuid NOT NULL,
"ProviderId" uuid NOT NULL,
"PayerId" uuid NOT NULL,
"Code" varchar(200) NOT NULL,
"Description" varchar(500) NOT NULL,
"EncounterClass" varchar(30) NOT NULL,
"Base_Encounter_Cost" decimal(18,2) NOT NULL,
"Total_Claim_Cost" decimal(18,2) NOT NULL,
"Payer_Coverage" decimal(18,2) NOT NULL,
"ReasonCode" varchar(200) null,
"ReasonDescription" varchar(500) null,

constraint "FK_ENCOUNTERS_PATIENTS" foreign key ("PatientId") references public."PATIENTS"("PatientId")
);

alter table public."ALLERGIES"
add constraint "FK_ALLERGIES_ENCOUNTERS" foreign key ("EncounterId") references public."ENCOUNTERS"("EncounterId");




--create ORGANIZATIONS table with default, common syntax
CREATE TABLE public."ORGANIZATIONS"(
"OrganizationId" uuid not null primary key,
"Name" varchar(200) not null,
"Address" varchar(300) not null,
"City" varchar(300) not null,
"Lattitude" varchar(20) null,
"Longitude" varchar(20) null,
"Revenue" decimal(18,2) not null,
"Utilization" integer not null
);

ALTER TABLE public."ENCOUNTERS"
add constraint "FK_ENCOUNTERS_ORGANIZATIONS" foreign key ("OrganizationId") references public."ORGANIZATIONS"("OrganizationId");




--create PROVIDERS table with default, common syntax
CREATE TABLE public."PROVIDERS"(
    "ProviderId" uuid not null PRIMARY KEY,
    "OrganizationId" uuid not null,
    "Name" varchar(200) not null,
    "Gender" char(1) NOT NULL,
    "Speciality" varchar(150) NOT NULL,
    "Address" varchar(300) NOT NULL,
    "City" varchar(200) NOT NULL,
constraint "FK_PROVIDERS_ORGANIZATION" foreign key ("OrganizationId") references public."ORGANIZATIONS"("OrganizationId")
);

alter table public."ENCOUNTERS"
add constraint "FK_ENCOUNTERS_PROVIDERS" foreign key ("ProviderId") references public."PROVIDERS"("ProviderId");




--create PAYERS table with default, common syntax
CREATE TABLE public."PAYERS"(
    "PayerId" uuid not null PRIMARY KEY,
    "Name" varchar(200) not null,
    "Ownership" varchar(30) null,
    "Address" varchar(300) null,
    "City" varchar(200) null,
    "Phone" varchar(100) null
);
alter table public."ENCOUNTERS"
add constraint "FK_ENCOUNTERS_PAYERS" foreign key ("PayerId") REFERENCES public."PAYERS"("PayerId");



--create CONDITIONS table with default, common syntax
CREATE TABLE public."CONDITIONS"(
    "ConditionId" uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    "PatientId" uuid NOT NULL,
    "EncounterId" uuid NOT NULL,
    "StartDate" date NOT NULL,
    "EndDate" date NULL,
    "System" varchar(50) NOT NULL,
    "Code" varchar(200) NOT NULL,
    "Description" varchar(500) NOT NULL,

    CONSTRAINT "FK_CONDITIONS_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_CONDITIONS_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId")
);



--create OBSERVATIONS table with default, common syntax
CREATE TABLE public."OBSERVATIONS" (
    "ObservationId" uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    "PatientId" uuid not null,
    "EncounterId" uuid NULL,
    "ObservationDate" timestamp(0) NOT NULL,
    "Category" VARCHAR(100) NULL,
    "Code" varchar(200) NOT NULL,
    "Description" varchar(500) NOT NULL,
    "Value" varchar NOT NULL,
    "Units" varchar(100) NULL,
    "Type" varchar(20) NOT NULL,

    CONSTRAINT "FK_OBSERVATIONS_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_OBSERVATIONS_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId")
);



--create PROCEDURES table with default, common syntax    
CREATE TABLE public."PROCEDURES" (
    "ProcedureId" uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    "PatientId" uuid NOT NULL,
    "EncounterId" uuid NOT NULL,
    "StartDate" timestamp(0) NOT NULL,
    "EndDate" timestamp(0) NULL,
    "System" varchar(50) NOT NULL,
    "Code" varchar(200) NOT NULL,
    "Description" varchar(500) NOT NULL,
    "Base_Cost" decimal(18,2) NOT NULL,
    "ReasonCode" varchar(200) NULL,
    "ReasonDescription" varchar(500) NULL,

    CONSTRAINT "FK_PROCEDURES_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_PROCEDURES_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId")
);



--create MEDICATIONS table with default, common syntax    
CREATE TABLE public."MEDICATIONS"(
    "MedicationId" uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    "PatientId" uuid NOT NULL,
    "EncounterId" uuid NOT NULL,
    "PayerId" uuid NOT NULL,
    "StartDate" timestamp(0) NOT NULL,
    "EndDate" timestamp(0) NULL,
    "Code" varchar(200) NOT NULL,
    "Description" varchar(500) NOT NULL,
    "Base_Cost" decimal(18,2) NOT NULL,
    "Payer_Coverage" decimal(18,2) NOT NULL,
    "Dispenses" int NOT NULL,
    "TotalCost" decimal(18,2) NOT NULL,
    "ReasonCode" varchar(200) NULL,
    "ReasonDescription" varchar(500) NULL,

    CONSTRAINT "FK_MEDICATIONS_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_MEDICATIONS_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId"),
    CONSTRAINT "FK_MEDICATIONS_PAYERS" FOREIGN KEY ("PayerId") REFERENCES public."PAYERS"("PayerId")
);




--create CLAIMS table with default, common syntax    
CREATE TABLE public."CLAIMS" (
    "ClaimId" uuid NOT NULL PRIMARY KEY,
    "PatientId" uuid NOT NULL,
    "ProviderId" uuid NOT NULL,
    "EncounterId" uuid NULL,
    "PrimaryPayerId" uuid NULL,
    "SecondaryPayerId" uuid NULL,
    "CurrentIllnessDate" timestamp(0) NOT NULL,
    "ServiceDate" timestamp(0) NOT NULL,
    "Diagnosis1" varchar(200) NULL,
    "Diagnosis2" varchar(200) NULL,
    "Diagnosis3" varchar(200) NULL,
    "Diagnosis4" varchar(200) NULL,
    "Diagnosis5" varchar(200) NULL,
    "Diagnosis6" varchar(200) NULL,
    "Diagnosis7" varchar(200) NULL,
    "Diagnosis8" varchar(200) NULL,
    "Status1" varchar(20) NULL,
    "Status2" varchar(20) NULL,
    "StatusP" varchar(20) NULL,
    "Outstanding1" decimal(18,2) NULL,
    "Outstanding2" decimal(18,2) NULL,
    "OutstandingP" decimal(18,2) NULL,
    "LastBilledDate1" timestamp(0) NULL,
    "LastBilledDate2" timestamp(0) NULL,
    "LastBilledDateP" timestamp(0) NULL,

    CONSTRAINT "FK_CLAIMS_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_CLAIMS_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId"),
    CONSTRAINT "FK_CLAIMS_PROVIDERS" FOREIGN KEY ("ProviderId") REFERENCES public."PROVIDERS"("ProviderId"),
    CONSTRAINT "FK_CLAIMS_PRIMARY_PAYERS" FOREIGN KEY ("PrimaryPayerId") REFERENCES public."PAYERS"("PayerId"),
    CONSTRAINT "FK_CLAIMS_SECONDARY_PAYERS" FOREIGN KEY ("SecondaryPayerId") REFERENCES public."PAYERS"("PayerId")
);



--create CLAIMS_TRANSACTIONS table with default, common syntax    
CREATE TABLE public."CLAIMS_TRANSACTIONS"(
    "ClaimTransactionId" uuid NOT NULL PRIMARY KEY,
    "ClaimId" uuid NOT NULL,
    "PatientId" uuid NOT NULL,
    "EncounterId" uuid NULL,
    "OrganizationId" uuid NOT NULL,
    "ProviderId" uuid NOT NULL,
    "ChargeId" bigint NOT NULL,
    "TransactionType" varchar(20) NOT NULL,
    "Amount" decimal(18,2) NULL,
    "Method" varchar(20) NULL,
    "FromDate" timestamp(0) NULL,
    "ToDate" timestamp(0) NULL,
    "ProcedureCode" varchar(200) NOT NULL,
    "Units" decimal(18,3) NULL,
    "UnitAmount" decimal(18,2) NULL,
    "DiagnosisRef1" smallint NULL,
    "DiagnosisRef2" smallint NULL,
    "DiagnosisRef3" smallint NULL,
    "DiagnosisRef4" smallint NULL,
    "Payments" decimal(18,2) NULL,
    "Adjustments" decimal(18,2) NULL,
    "Transfers" decimal(18,2) NULL,
    "Outstanding" decimal(18,2) NULL,
    "TransferOutId" bigint NULL,
    "TransferType" varchar(10) NULL,
    "Notes" varchar(1000) NULL,
    "LineNote" varchar(1000) NULL,

    CONSTRAINT "FK_CLAIMS_TRANSACTIONS_CLAIMS" FOREIGN KEY ("ClaimId") REFERENCES public."CLAIMS"("ClaimId"),
    CONSTRAINT "FK_CLAIMS_TRANSACTIONS_PATIENTS" FOREIGN KEY ("PatientId") REFERENCES public."PATIENTS"("PatientId"),
    CONSTRAINT "FK_CLAIMS_TRANSACTIONS_ENCOUNTERS" FOREIGN KEY ("EncounterId") REFERENCES public."ENCOUNTERS"("EncounterId"),
    CONSTRAINT "FK_CLAIMS_TRANSACTIONS_ORGANIZATIONS" FOREIGN KEY ("OrganizationId") REFERENCES public."ORGANIZATIONS"("OrganizationId"),
    CONSTRAINT "FK_CLAIMS_TRANSACTIONS_PROVIDERS" FOREIGN KEY ("ProviderId") REFERENCES public."PROVIDERS"("ProviderId")
);