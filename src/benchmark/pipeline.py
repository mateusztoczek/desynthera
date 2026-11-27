from pathlib import Path


def run(target:str, command: str, **params):
    if command=="measure":
        if target not in ("postgres","postgress"): raise ValueError(f"Measurement not supported for: {target}")
        from benchmark import measure_postgres
        return measure_postgres.run(**params)
    if command=="measure_call":
        if target not in ("postgres","postgress"): raise ValueError(f"Measurement not supported for: {target}")
        from benchmark import measure_postgres
        return measure_postgres.run_call(**params)

    match target:
        case "sqlserver":
            from benchmark.database import sqlserver
            bck=sqlserver
        case "postgres" | "postgress":
            if command=="measure":
                from benchmark import measure_postgres
                return measure_postgres.run(**params)
            if command=="measure_call":
                from benchmark import measure_postgres
                return measure_postgres.run_call(**params)
            from benchmark.database import postgres
            bck=postgres
        case _:
            raise ValueError(f"Not supported: {target}")

    match command:
        case "fix_observation":
            return bck.fix_observation(**params)
        case "remove_medication":
            return bck.remove_medication(**params)
        case "register_patient_death":
            return bck.register_patient_death(**params)
        case "register_new_allergy":
            return bck.register_new_allergy(**params)
        case _:
            raise ValueError(f"Not supported: {command}")
                    