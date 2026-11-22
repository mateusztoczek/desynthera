from pathlib import Path
import polars as pl
import re
from etl.schema import T_SCHEMA
from etl.transformation import p_transform
from etl.validattion import p_validate

DEFAULT_OUTPUT=Path.cwd()/"output"


def r_validate_df_id(df_id:str)->str:
    if not isinstance(df_id,str): raise TypeError("String type required")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}",df_id): raise ValueError("Wrong dataset id format")
    return df_id


def run(df_id:str, input_dir: Path, output_dir: Path | None=None)-> None:
    df_id=r_validate_df_id(df_id)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Path doesnt exists: {input_dir}")
    target_dir=output_dir if output_dir is not None else DEFAULT_OUTPUT
    target_dir.mkdir(parents=True, exist_ok=True)

    for t_csv in sorted(input_dir.glob("*.csv")):
        t_name=t_csv.stem.lower()
        if t_name not in T_SCHEMA: continue
        df=pl.scan_csv(t_csv, infer_schema=False)
        df_resp=p_transform(df,T_SCHEMA[t_name], df_id)
        
        output_file=target_dir/f"{t_name}.parquet"
        tmp_file=target_dir/f"{t_name}.parquet.tmp"
        try:
            df_resp.sink_parquet(tmp_file)
            p_validate(pl.scan_parquet(tmp_file),T_SCHEMA[t_name])
            tmp_file.replace(output_file)
        except Exception:
            tmp_file.unlink(missing_ok=True)
            raise