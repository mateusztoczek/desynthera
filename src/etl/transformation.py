import polars as pl


def p_transform(df: pl.LazyFrame, t_map:dict)->pl.LazyFrame:
    missed=set(t_map["columns"])-set(df.collect_schema().names())
    if missed: raise ValueError(f"Columnes are missing: {sorted(missed)}")

    target_list=[]
    for t_src,t_conf in t_map["columns"].items():
        t_target=t_conf["target_name"]
        t_dtype=t_conf["type"]
        c=pl.col(t_src)
        match t_dtype:
            case "date":
                c=c.str.strptime(pl.Date,format="%Y-%m-%d",strict=True)
            case "integer":
                c=c.cast(pl.Int64,strict=True)
            case "decimal":
                c=c.cast(pl.Decimal(18,2), strict=True)
            case "uuid":
                pass
            case "text":
                pass
            case _:
                raise ValueError(f"unknown format: {t_dtype}")
        
        target_list.append(c.alias(t_target))
    return df.select(target_list)