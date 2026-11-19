from pathlib import Path


def run(target:str, command: str, **params):
    match target:
        case "sqlserver":
            from benchmark.database import sqlserver
            bck=sqlserver
        case "postgress":
            from benchmark.database import postgres
            bck=postgres
        case _:
            raise ValueError(f"Not supported: {target}")

    match command:
        case "fix_observation":
            return bck.fix_observation(**params)
        case "withdrawn_medication":
            bck.remove_medication(**params)
        case _:
            raise ValueError(f"Not supported: {command}")
                    