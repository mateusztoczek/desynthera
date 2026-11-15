import argparse
from etl.pipeline import run as run_pipe

def run()->None:
    parse= argparse.ArgumentParser()
    parse.add_argument("--df_id", required=True)
    parse.add_argument("--input_dir", required=True)
    parse.add_argument("--output_dir", default=None )

    args=parse.parse_args()
    run_pipe(args.df_id,args.input_dir, args.output_dir)