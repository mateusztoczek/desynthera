import argparse
import json
from pathlib import Path
from benchmark.pipeline import run as run_pipe
 
def run(argv: list[str] | None=None)->None:
    parse= argparse.ArgumentParser()
    parse.add_argument("--target", required=True)
    parse.add_argument("--command", required=True)
    parse.add_argument("--command_params", default="{}")

    args=parse.parse_args(argv)
    params=json.loads(args.params)
    if not isinstance(params,dict): parse.error("command_params must be JSON object")
    run_pipe(target=args.target,command=args.command, **params)