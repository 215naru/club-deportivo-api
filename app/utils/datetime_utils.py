import re
from datetime import datetime, timezone, timedelta

GMT3 = timezone(timedelta(hours=-3))
PATRON_FECHA_HORA = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$"
)

def parsear_fecha_hora(valor):
    if not isinstance(valor, str) or not PATRON_FECHA_HORA.match(valor):
        return None
    texto_sin_offset = valor[:-6]
    return datetime.strptime(texto_sin_offset, "%Y-%m-%dT%H:%M:%S.%f")

def formatear_fecha_hora(momento):
    return momento.strftime("%Y-%m-%dT%H:%M:%S.%f") + "-03:00"

def ahora_gmt3():
    return datetime.now(timezone.utc).astimezone(GMT3).replace(tzinfo=None)