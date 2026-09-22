from app.errors import ApiError

def obtener_paginacion(args):
    try:
        limit = int(args.get("_limit",10))
        offset = int(args.get("_offset",0))
    except ValueError:
        raise ApiError(400, "PAGINACION_INVALIDA","_limit y _offset deben ser números enteros")
    
    if limit <1 or limit >100:
        raise ApiError(400,"PAGINACION_INVALIDA","_limit debe estar entre 1 y 100")
    if offset <0:
        raise ApiError(400,"PAGINACION_INVALIDA","_offset debe ser mayor o igual a 0")
    
    return limit, offset

def construir_links(base_url,limit,offset,total):
    links = {
        "_first":{"href":f"{base_url}?_limit={limit}?_offset=0"}
    }

    if offset > 0:
        anterior = max(offset - limit,0)
        links["_prev"] = {"href":f"{base_url}?_limit={limit}?_offset={anterior}"}
    
    siguiente = offset + limit
    if siguiente < total:
        links["_next"] = {"href": f"{base_url}?_limit={limit}&_offset={siguiente}"}

    if total > 0:
        ultimo = ((total - 1) // limit) * limit
        links["_last"] = {"href": f"{base_url}?_limit={limit}&_offset={ultimo}"}

    return links