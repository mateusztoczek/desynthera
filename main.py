import sys
import argparse
from etl.cli import run_etl
from importer.cli import run_import

def main():
    if len(sys.argv)<2: raise ValueError("Wrong usage")
    m_cmd=sys.argv[1]
    m_args=sys.argv[2:]
    match m_cmd:
        case "transform":
            run_etl(m_args)
        case "load":
            run_import(m_args)
        case _:
            raise SystemExit(f"Unknown command: {m_cmd}")

if __name__=="__main__":
    main()