from pathlib import Path


def run(target:str, input_dir: Path, b_size: int):
    if not input_dir.is_dir(): raise FileNotFoundError(f"Path doesnt exists: {input_dir}")
    match target:
        case "sqlserver":
            from importer.database.sqlserver import load
        case "postgres" | "postgress":
            from importer.database.postgres import load
        case "mongodb":
            from importer.database.mongodb import load
        case "cassandra":
            from importer.database.cassandra import load
        case _:
            raise ValueError(f"Not supported: {target}")

    load(input_dir,b_size)  
                    