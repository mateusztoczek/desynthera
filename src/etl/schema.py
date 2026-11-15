T_SCHEMA={
    "patients":{
        "Id": ("PatientId", "uuid"),
        "BIRTHDATE": ("BirthDate", "date"),
        "DEATHDATE": ("DeathDate", "date"),
        "SSN": ("SSN",'text'),
        "FIRST":("FirstName","text"),
        "LAST":("LastName","text"),
        "SUFFIX":("Suffix","text"),
        "MARITAL":("MaritalStatus","text"),
        "RACE":("Race","text"),
        "GENDER":("Gender","text"),
        "ADDRESS":("Address","text"),
        "CITY":("City","text")
    },
    "allergies":{
        
        "PATIENT":("PatientId","uuid"),
        "ENCOUNTER":("EncounterId","uuid"),
        "START":("StartDate","date"),
        "END":("EndDate","date"),
        "CODE":("Code","text"),
        "SYSTEM":("System","text"),
        "DESCRIPTION":("Description","text"),
        "TYPE":("Type","text"),
        "CATEGORY":("Category", "text"),
        "REACTION1":("Reaction1","text"),
        "DESCRIPTION1":("Description1","text"),
        "SEVERITY1":("Severity1","text"),
        "REACTION2":("Reaction2","text"),
        "DESCRIPTION2":("Description2","text"),
        "SEVERITY2":("Severity2","text")        
    }
}

