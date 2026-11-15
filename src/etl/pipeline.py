from pathlib import Path
import polars as pl
from etl.schema import T_SCHEMA
from etl.transformation import p_transform

DEFAULT_OUTPUT=Path.cwd()/"output"

def run(input_dir: Path, output_dir: Path | None=None)-> None:
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Path doesnt exists: {input_dir}")
    target_dir=DEFAULT_OUTPUT
    if output_dir is not None:
        try:
            output_dir.mkdir(parents=True,exist_ok=True)
            target_dir=output_dir
        except OSError: print(f"wrong output direction: {output_dir}, using default {DEFAULT_OUTPUT}")
    target_dir.mkdir(parents=True, exist_ok=True)

    for t_csv in sorted(input_dir.glob("*.csv")):
        t_name=t_csv.stem.lower()
        if t_name not in T_SCHEMA: continue
        df=pl.scan_csv(t_csv, infer_schema=False)
        df_resp=p_transform(df,T_SCHEMA[t_name])

        output_file=target_dir/f"{t_name}.parquet"
        df_resp.sink_parquet(output_file)