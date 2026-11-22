import argparse
from pathlib import Path
from importer.pipeline import run as run_pipe
 
def run(argv: list[str] | None=None)->None:
    parse= argparse.ArgumentParser()
    parse.add_argument("--target", required=True)
    parse.add_argument("--input_dir", required=True)
    parse.add_argument("--batch_size", type=int, default=1000)

    args=parse.parse_args(argv)
    run_pipe(target=args.target,input_dir=Path(args.input_dir), b_size=args.batch_size)