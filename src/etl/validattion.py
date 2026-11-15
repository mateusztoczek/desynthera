import polars as pl


UUID_REG=(r"(?i)^[0-9a-f]{8}-[0-9a-f]{4}-"r"[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

REQ_TYPE= {
    "date": pl.Date,
    "datetime": pl.Datetime("us"),
    "uuid": pl.String,
    "text": pl.String,
    "integer": pl.Int64,
    "decimal": pl.Decimal(18, 2)
}


def p_check_nnull(df: pl.LazyFrame,c_name: str) ->None:
    c = pl.col(c_name)
    invalid=c.is_null()

    if df.collect_schema()[c_name]==pl.String: invalid=invalid | (c.str.strip_chars()=="").fill_null(False)
    count= df.select(invalid.sum()).collect().item()
    if count>0: raise ValueError(f"{c_name}: {count} missing")


def p_check_type(df: pl.LazyFrame, c_name: str, t_dtype: str)->None:
    expected= REQ_TYPE[t_dtype]
    present =df.collect_schema()[c_name]
    if present!=expected:raise TypeError(f"{c_name}: expected {expected}, got {present}")


def p_check_uuid(df: pl.LazyFrame, c_name: str)->None:
    c=pl.col(c_name)
    invalid= (c.is_not_null() & (~c.str.contains(UUID_REG).fill_null(True)))
    count=df.select(invalid.sum()).collect().item()
    if count>0: raise ValueError(f"{c_name}: {count} invalid UUID")


def p_check_unique(df: pl.LazyFrame,c_name: str)->None:
    row_total, row_uniq=df.select(pl.len(), pl.col(c_name).n_unique()).collect().row(0)
    if row_total!=row_uniq: raise ValueError(f"{c_name} has {row_total-row_uniq} duplicates")


def p_validate(df: pl.LazyFrame, t_map:dict)-> None:
    expected_cols= {conf["target_name"] for conf in t_map["columns"].values()}
    missed= expected_cols-set(df.collect_schema().names())
    if missed: raise ValueError(f"Columnes are missing: {sorted(missed)}")

    for t_src,t_conf in t_map["columns"].items():
        t_target=t_conf["target_name"]
        t_dtype=t_conf["type"]
        p_check_type(df,t_target,t_dtype)
        if t_conf["required"]: p_check_nnull(df,t_target)
        if t_dtype=="uuid": p_check_uuid(df,t_target)
        pk=t_map.get("primary_key")
        if pk:
            if pk not in df.collect_schema(): raise ValueError(f"primary key is missing: {pk}")
            p_check_nnull(df,pk)
            p_check_unique(df,pk)
    return