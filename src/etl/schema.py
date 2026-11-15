T_SCHEMA={
    "patients":{
        "columns":{
            "Id": {"target_name": "PatientId", "type": "uuid", "required": True},
            "BIRTHDATE": {"target_name": "BirthDate", "type": "date", "required": True},
        "DEATHDATE": {"target_name": "DeathDate", "type": "date", "required": False},
            "SSN": {"target_name": "SSN", "type": "text", "required": False},
            "FIRST": {"target_name": "FirstName", "type": "text", "required": True},
            "LAST": {"target_name": "LastName", "type": "text", "required": True},
            "SUFFIX": {"target_name": "Suffix", "type": "text", "required": False},
            "MARITAL": {"target_name": "MaritalStatus", "type": "text", "required": False},
            "RACE": {"target_name": "Race", "type": "text", "required": True},
            "GENDER": {"target_name": "Gender", "type": "text", "required": True},
            "ADDRESS": {"target_name": "Address", "type": "text", "required": True},
            "CITY": {"target_name": "City", "type": "text", "required": True},
        },
        "primary_key":"PatientId"                
    },
    "allergies":{
        "columns":{

            "PATIENT": {"target_name": "PatientId", "type": "uuid", "required": True},
            "ENCOUNTER": {"target_name": "EncounterId", "type": "uuid", "required": True},
            "START": {"target_name": "StartDate", "type": "date", "required": True},
            "STOP": {"target_name": "EndDate", "type": "date", "required": False},
            "CODE": {"target_name": "Code", "type": "text", "required": True},
            "SYSTEM": {"target_name": "System", "type": "text", "required": True},
            "DESCRIPTION": {"target_name": "Description", "type": "text", "required": True},
            "TYPE": {"target_name": "Type", "type": "text", "required": False},
            "CATEGORY": {"target_name": "Category", "type": "text", "required": False},
            "REACTION1": {"target_name": "Reaction1", "type": "text", "required": False},
            "DESCRIPTION1": {"target_name": "Description1", "type": "text", "required": False},
            "SEVERITY1": {"target_name": "Severity1", "type": "text", "required": False},
            "REACTION2": {"target_name": "Reaction2", "type": "text", "required": False},
            "DESCRIPTION2": {"target_name": "Description2", "type": "text", "required": False},
            "SEVERITY2": {"target_name": "Severity2", "type": "text", "required": False}            
        },
        "primary_key": "AllergiesId",
        "generated_id":{"target_name":"AllergiesId", "strategy":"uuid5"}
    },
    "encounters":{
         "columns":{    
            "Id": {"target_name": "EncounterId", "type": "uuid", "required": True},
            "PATIENT": {"target_name": "PatientId", "type": "uuid", "required": True},
            "START": {"target_name": "StartDate", "type": "datetime", "required": True},
            "STOP": {"target_name": "EndDate", "type": "datetime", "required": False},
            "ORGANIZATION": {"target_name": "OrganizationId", "type": "uuid", "required": True},
            "PROVIDER": {"target_name": "ProviderId", "type": "uuid", "required": True},
            "PAYER": {"target_name": "PayerId", "type": "uuid", "required": True},
            "CODE": {"target_name": "Code", "type": "text", "required": True},
            "DESCRIPTION": {"target_name": "Description", "type": "text", "required": True},
            "ENCOUNTERCLASS": {"target_name": "EncounterClass", "type": "text", "required": True},
            "BASE_ENCOUNTER_COST": {"target_name": "Base_Encounter_Cost", "type": "decimal", "required": True},
            "TOTAL_CLAIM_COST": {"target_name": "Total_Claim_Cost", "type": "decimal", "required": True},
            "PAYER_COVERAGE": {"target_name": "Payer_Coverage", "type": "decimal", "required": True},
            "REASONCODE": {"target_name": "ReasonCode", "type": "text", "required": False},
            "REASONDESCRIPTION": {"target_name": "ReasonDescription", "type": "text", "required": False}            
        },
        "primary_key": "EncounterId"
    },
    "organizations": {
        "columns": {
            "Id": {"target_name": "OrganizationId", "type": "uuid", "required": True},
            "NAME": {"target_name": "Name", "type": "text", "required": True},
            "ADDRESS": {"target_name": "Address", "type": "text", "required":True},
            "CITY": {"target_name": "City", "type": "text", "required": True},
            "LAT": {"target_name": "Lattitude", "type":"text", "required":False},
            "LON": {"target_name": "Longitude", "type":"text", "required":False},
            "REVENUE": {"target_name": "Revenue", "type": "decimal", "required": True},
            "UTILIZATION": {"target_name": "Utilization","type": "integer","required": True}
        },
        "primary_key": "OrganizationId"
    },
    "providers": {
        "columns": {
            "Id": {"target_name":"ProviderId", "type": "uuid", "required":True},
            "ORGANIZATION":{"target_name": "OrganizationId","type": "uuid","required": True},
            "NAME":{"target_name": "Name","type":"text", "required":True},
            "GENDER":{"target_name": "Gender", "type": "text", "required": True},
            "SPECIALITY":{"target_name":"Speciality", "type": "text","required":True},
            "ADDRESS":{"target_name": "Address", "type": "text","required":True},
            "CITY":{"target_name": "City","type": "text","required": True}
        },
        "primary_key": "ProviderId"
    },
    "payers": {
        "columns": {
            "Id": {"target_name": "PayerId", "type":"uuid", "required":True},
            "NAME": {"target_name": "Name", "type": "text","required": True},
            "OWNERSHIP": {"target_name":"Ownership", "type": "text","required": False},
            "ADDRESS": {"target_name": "Address", "type": "text","required": False},
            "CITY": {"target_name": "City","type": "text","required":False},
            "PHONE": {"target_name": "Phone","type":"text", "required": False}
        },
        "primary_key": "PayerId"
    },
    "conditions": {
        "columns": {
            "PATIENT": {"target_name":"PatientId","type":"uuid","required": True},
            "ENCOUNTER": {"target_name": "EncounterId","type":"uuid", "required": True},
            "START": {"target_name": "StartDate","type": "date", "required": True},
            "STOP": {"target_name": "EndDate","type": "date", "required": False},
            "SYSTEM": {"target_name":"System", "type": "text", "required": True},
            "CODE": {"target_name":"Code", "type": "text", "required": True},
            "DESCRIPTION":{"target_name": "Description", "type": "text", "required": True}
        },
        "primary_key": "ConditionId",
        "generated_id": {"target_name":"ConditionId","strategy": "uuid5"}
    },
    "observations": {
        "columns": {
            "PATIENT": {"target_name": "PatientId", "type": "uuid", "required": True},
            "ENCOUNTER":{"target_name": "EncounterId", "type": "uuid", "required": True},
            "DATE": {"target_name":"ObservationDate","type":"datetime", "required": True},
            "CATEGORY": {"target_name": "Category", "type": "text", "required": False},
            "CODE": {"target_name": "Code","type":"text","required": True},
            "DESCRIPTION":{"target_name": "Description", "type": "text", "required": True},
            "VALUE": {"target_name": "Value","type": "text", "required": True},
            "UNITS":{"target_name": "Units", "type": "text", "required": False},
            "TYPE": {"target_name": "Type", "type": "text", "required": True}
        },
        "primary_key": "ObservationId",
        "generated_id":{"target_name": "ObservationId","strategy": "uuid5"}
    },
    "procedures": {
        "columns": {
            "PATIENT": {"target_name":"PatientId", "type": "uuid", "required": True},
            "ENCOUNTER": {"target_name": "EncounterId", "type": "uuid","required":True},
            "START": {"target_name": "StartDate", "type": "datetime","required":True},
            "STOP": {"target_name": "EndDate", "type": "datetime", "required": False},
            "SYSTEM": {"target_name":"System", "type": "text", "required": True},
            "CODE": {"target_name": "Code","type":"text","required": True},
            "DESCRIPTION": {"target_name":"Description","type":"text", "required": True},
            "BASE_COST": {"target_name": "Base_Cost", "type": "decimal", "required": True},
            "REASONCODE": {"target_name":"ReasonCode", "type": "text", "required": False},
            "REASONDESCRIPTION": {"target_name": "ReasonDescription", "type": "text", "required": False}
        },
        "primary_key": "ProcedureId",
        "generated_id":{"target_name":"ProcedureId","strategy": "uuid5"}
    },
    "medications": {
        "columns": {
            "PATIENT": {"target_name": "PatientId","type": "uuid", "required": True},
            "ENCOUNTER":{"target_name": "EncounterId","type": "uuid", "required": True},
            "PAYER": {"target_name":"PayerId", "type": "uuid", "required": True},
            "START": {"target_name":"StartDate", "type":"datetime", "required": True},
            "STOP": {"target_name":"EndDate", "type": "datetime", "required": False},
            "CODE":{"target_name":"Code", "type": "text","required": True},
            "DESCRIPTION": {"target_name":"Description", "type": "text", "required": True},
            "BASE_COST": {"target_name":"Base_Cost", "type": "decimal", "required": True},
            "PAYER_COVERAGE": {"target_name":"Payer_Coverage", "type": "decimal", "required": True},
            "DISPENSES":{"target_name":"Dispenses", "type":"integer", "required": True},
            "TOTALCOST":{"target_name":"TotalCost", "type":"decimal", "required": True},
            "REASONCODE": {"target_name":"ReasonCode", "type": "text", "required": False},
            "REASONDESCRIPTION": {"target_name":"ReasonDescription", "type": "text", "required": False}
        },
        "primary_key": "MedicationId",
        "generated_id": {"target_name": "MedicationId","strategy": "uuid5"}
    },
    "claims": {
        "columns": {
            "Id": {"target_name": "ClaimId", "type": "uuid", "required": True},
            "PATIENTID": {"target_name": "PatientId", "type": "uuid", "required": True},
            "PROVIDERID": {"target_name": "ProviderId", "type": "uuid", "required": True},
            "APPOINTMENTID": {"target_name": "EncounterId", "type": "uuid", "required": False},
            "PRIMARYPATIENTINSURANCEID": {"target_name":"PrimaryPayerId", "type": "uuid", "required": False},
            "SECONDARYPATIENTINSURANCEID": {"target_name": "SecondaryPayerId", "type": "uuid", "required": False},
            "CURRENTILLNESSDATE": {"target_name": "CurrentIllnessDate", "type": "datetime", "required": True},
            "SERVICEDATE": {"target_name": "ServiceDate", "type": "datetime", "required": True},
            "DIAGNOSIS1": {"target_name": "Diagnosis1", "type": "text", "required":False},
            "DIAGNOSIS2": {"target_name": "Diagnosis2", "type": "text", "required": False},
            "DIAGNOSIS3": {"target_name": "Diagnosis3", "type": "text", "required": False},
            "DIAGNOSIS4": {"target_name": "Diagnosis4", "type": "text", "required":False},
            "DIAGNOSIS5": {"target_name": "Diagnosis5", "type": "text", "required": False},
            "DIAGNOSIS6": {"target_name": "Diagnosis6", "type": "text", "required": False},
            "DIAGNOSIS7": {"target_name": "Diagnosis7", "type": "text", "required":False},
            "DIAGNOSIS8": {"target_name": "Diagnosis8", "type": "text", "required": False},
            "STATUS1": {"target_name": "Status1","type": "text", "required":False},
            "STATUS2": {"target_name": "Status2","type": "text", "required": False},
            "STATUSP": {"target_name": "StatusP","type": "text", "required": False},
            "OUTSTANDING1": {"target_name": "Outstanding1", "type": "decimal", "required": False},
            "OUTSTANDING2": {"target_name": "Outstanding2", "type": "decimal","required": False},
            "OUTSTANDINGP": {"target_name": "OutstandingP", "type": "decimal", "required": False},
            "LASTBILLEDDATE1": {"target_name":"LastBilledDate1", "type": "datetime", "required": False},
            "LASTBILLEDDATE2": {"target_name":"LastBilledDate2", "type":"datetime", "required": False},
            "LASTBILLEDDATEP": {"target_name":"LastBilledDateP", "type": "datetime", "required": False}
        },
        "primary_key": "ClaimId"
    },
    "claims_transactions": {
        "columns": {
            "ID": {"target_name": "ClaimTransactionId", "type": "uuid", "required": True},
            "CLAIMID": {"target_name": "ClaimId", "type": "uuid", "required": True},
            "PATIENTID": {"target_name": "PatientId", "type": "uuid", "required": True},
            "APPOINTMENTID": {"target_name": "EncounterId", "type": "uuid", "required": False},
            "PLACEOFSERVICE": {"target_name": "OrganizationId", "type": "uuid", "required": True},
            "PROVIDERID": {"target_name": "ProviderId", "type": "uuid", "required": True},
            "CHARGEID": {"target_name": "ChargeId", "type": "integer", "required": True},
            "TYPE": {"target_name": "TransactionType", "type": "text", "required": True},
            "AMOUNT":{"target_name": "Amount","type": "decimal", "required": False},
            "METHOD":{"target_name": "Method","type": "text", "required": False},
            "FROMDATE": {"target_name": "FromDate", "type": "datetime", "required": False},
            "TODATE": {"target_name": "ToDate", "type": "datetime", "required": False},
            "PROCEDURECODE": {"target_name": "ProcedureCode","type": "text", "required": True},
            "UNITS": {"target_name": "Units", "type":"decimal3", "required": False},
            "UNITAMOUNT": {"target_name": "UnitAmount","type": "decimal", "required": False},
            "DIAGNOSISREF1": {"target_name":"DiagnosisRef1","type": "integer", "required": False},
            "DIAGNOSISREF2": {"target_name":"DiagnosisRef2","type": "integer", "required": False},
            "DIAGNOSISREF3": {"target_name":"DiagnosisRef3","type": "integer", "required": False},
            "DIAGNOSISREF4": {"target_name":"DiagnosisRef4","type": "integer", "required": False},
            "PAYMENTS": {"target_name":"Payments", "type": "decimal", "required": False},
            "ADJUSTMENTS": {"target_name":"Adjustments", "type":"decimal", "required": False},
            "TRANSFERS": {"target_name":"Transfers", "type":"decimal", "required": False},
            "OUTSTANDING": {"target_name":"Outstanding", "type":"decimal", "required": False},
            "TRANSFEROUTID": {"target_name":"TransferOutId","type": "integer", "required": False},
            "TRANSFERTYPE": {"target_name":"TransferType","type": "text", "required": False},
            "NOTES": {"target_name": "Notes","type": "text","required": False},
            "LINENOTE": {"target_name": "LineNote", "type":"text", "required": False}
        },
        "primary_key": "ClaimTransactionId"
    }
}
