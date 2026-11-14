from pathlib import Path
import polars as pl

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

    for f_csv in sorted(input_dir.glob("*.csv")):
        df=pl.scan_csv(f_csv, infer_schema=False)
        output_file=target_dir/f"{f_csv.stem}.parquet"
        df.sink_parquet(output_file)