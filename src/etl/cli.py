import argparse
from pathlib import Path
from etl.pipeline import run as run_pipe

def run(argv: list[str] | None=None)->None:
    parse= argparse.ArgumentParser()
    parse.add_argument("--df_id", required=True)
    parse.add_argument("--input_dir", required=True)
    parse.add_argument("--output_dir", default=None )

    args=parse.parse_args(argv)
    run_pipe(df_id=args.df_id,input_dir=Path(args.input_dir), output_dir=Path(args.output_dir) if args.output_dir else None)