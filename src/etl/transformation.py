import polars as pl
from uuid import uuid5, NAMESPACE_URL


def p_generate_uuid(df_id: str, t_name: str, r_idx: int)->str:
    ident=f"desynthea:{df_id}:{t_name}:{r_idx}"
    return str(uuid5(NAMESPACE_URL,ident))


def p_transform(df: pl.LazyFrame, t_map:dict,df_id:str)->pl.LazyFrame:
    missed=set(t_map["columns"])-set(df.collect_schema().names())
    if missed: raise ValueError(f"Columnes are missing: {sorted(missed)}")

    t_generated=t_map.get("generated_id")
    if t_generated: df=df.with_row_index("__source_row")
    
    target_list=[]
    for t_src,t_conf in t_map["columns"].items():
        t_target=t_conf["target_name"]
        t_dtype=t_conf["type"]
        c=pl.col(t_src)
        match t_dtype:
            case "date":
                c=c.str.strptime(pl.Date,format="%Y-%m-%d",strict=True)
            case "datetime":
                c=c.str.to_datetime(time_unit="us",time_zone="UTC", strict=True).dt.replace_time_zone(None)
            case "integer":
                c=c.cast(pl.Int64,strict=True)
            case "decimal":
                c=c.cast(pl.Decimal(18,2), strict=True)
            case "decimal3":
                c=c.cast(pl.Decimal(18,3), strict=True)
            case "uuid":
                pass
            case "text":
                pass
            case _:
                raise ValueError(f"unknown format: {t_dtype}")
        
        target_list.append(c.alias(t_target))

    if t_generated:
        if t_generated["strategy"]!="uuid5":
            raise ValueError("strategy not supported")
        id_name=t_generated["target_name"]
        generated_c=(pl.col("__source_row").map_elements(lambda r: p_generate_uuid(df_id,id_name,r), return_dtype=pl.String).alias(id_name))
        target_list.insert(0,generated_c)
    return df.select(target_list)