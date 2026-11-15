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
            "END": {"target_name": "EndDate", "type": "date", "required": False},
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
        "generated_id":{"target_anme":"AllergiesId", "strategy":"uuid5"}
    }
}

