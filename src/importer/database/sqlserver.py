import os
from contextlib import closing
from pathlib import Path
import pyodbc
import pyarrow.parquet as pq


T_TABLES=("patients", "organizations", "payers", "providers", "encounters", 
        "allergies", "conditions","observations", "procedures", "medications","claims","claims_transactions"
)
  

def load(input_dir: Path, b_size: int=1000)->None:
    if not input_dir.is_dir(): raise FileNotFoundError(input_dir)
    if b_size<=0: raise ValueError("Batch size too small")
    conn_str= os.environ.get("SQLSERVER_CONNECTION")
    if not conn_str: raise ValueError("SQL SERVER connection not configured")

    for t in T_TABLES:
        path=input_dir/f"{t}.parquet"
        if not path.is_file(): raise FileNotFoundError(path)
    
    with closing(pyodbc.connect(conn_str, autocommit=False)) as conn:
        cur=conn.cursor()
        cur.fast_executemany=True
        try:
            for t in T_TABLES:
                path=input_dir/f"{t}.parquet"
                parquet=pq.ParquetFile(path)
                try:
                    cols=parquet.schema_arrow.names
                    cols_names= ", ".join(f"[{c.replace(']',']]')}]" for c in cols)
                    temp_place=", ".join("?" for _ in cols)
                    s_command=(f"INSERT INTO dbo.[{t.upper()}] "f"({cols_names}) "f"VALUES ({temp_place});")
                    rows_done = 0
                    for batch in parquet.iter_batches(batch_size=b_size):
                        rows= [tuple(record[c] for c in cols)for record in batch.to_pylist()]
                        if not rows: continue
                        try:
                            cur.executemany(s_command, rows)
                            conn.commit()
                        except Exception:
                            conn.rollback()
                            raise

                        rows_done+= len(rows)
                        if rows_done %10000==0: print(f"{t}: {rows_done} rows parsed", flush=True)
                    print(f"{t}: all {rows_done} rows parsed")                
                finally:
                    parquet.close()
        finally:
            cur.close()