import polars as pl


def p_transform(df: pl.LazyFrame, t_map:dict)->pl.LazyFrame:
    missed=set(t_map)-set(df.collect_schema().names())
    if missed: raise ValueError(f"Columnes are missing: {sorted(missed)}")

    target_list=[]
    for i,(j,dtype) in t_map.items():
        c=pl.col(i)
        match dtype:
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
                raise ValueError(f"unknown format: {dtype}")
        
        target_list.append(c.alias(j))
    return df.select(target_list)