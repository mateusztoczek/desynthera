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


def p_validate(df: pl.LazyFrame,t_map: dict)->None:
    pres_schema = df.collect_schema()
    t_cols=[(conf["target_name"],conf["type"],conf["required"])for conf in t_map["columns"].values()]

    t_generated= t_map.get("generated_id")
    if t_generated: t_cols.append((t_generated["target_name"],"uuid", True))
    for t_name, t_dtype, t_required in t_cols:
        if t_name not in pres_schema: raise ValueError(f"Missing column: {t_name}")
        if pres_schema[t_name]!= REQ_TYPE[t_dtype]: raise TypeError(f"{t_name}: expected {REQ_TYPE[t_dtype]}, "f"got {pres_schema[t_name]}")

    checks=[pl.len().alias("row_count")]
    for t_name, t_dtype, t_required in t_cols:
        c = pl.col(t_name)
        if t_required:
            invalid= c.is_null()
            if t_dtype in ("uuid", "text"): invalid= invalid | (c.str.strip_chars() == "").fill_null(False)
            checks.append(invalid.sum().alias(f"missing:{t_name}"))

        if t_dtype== "uuid":
            invalid_uuid= (c.is_not_null() & (c.str.strip_chars() != "").fill_null(False) & ~c.str.contains(UUID_REG).fill_null(False))
            checks.append(invalid_uuid.sum().alias(f"uuid:{t_name}"))

    pk=t_map.get("primary_key")
    if pk:
        if pk not in pres_schema: raise ValueError(f"Missing primary key: {pk}")
        checks.append(pl.col(pk).n_unique().alias("unique_pk"))

    result= (df.select(checks).collect(engine="streaming").row(0, named=True))

    errs=[]
    for key, value in result.items():
        if key.startswith(("missing:", "uuid:")) and value>0: errs.append(f"{key}: {value} invalid values")

    if pk and result["row_count"]!= result["unique_pk"]: errs.append(f"Primary key {pk} is not unique")
    if errs: raise ValueError("Validation failed:\n" + "\n".join(errs))