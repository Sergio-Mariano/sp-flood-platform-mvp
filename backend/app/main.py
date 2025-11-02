from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import datetime

from app.etl.geosampa import merged_floods_geojson

# --------------------------------------------------------------------
# App e templates
# --------------------------------------------------------------------
app = FastAPI(title="SP Flood Platform (MVP)")

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")

# garante que a pasta de estáticos exista (evita erro de diretório inexistente)
os.makedirs(STATIC_DIR, exist_ok=True)

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --------------------------------------------------------------------
# Rotas básicas
# --------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "ts": datetime.datetime.utcnow().isoformat() + "Z"}

@app.get("/")
async def root():
    tmpl = env.get_template("index.html")
    return HTMLResponse(tmpl.render())

@app.get("/mapa")
async def mapa():
    tmpl = env.get_template("mapa.html")
    return HTMLResponse(tmpl.render())


# --------------------------------------------------------------------
# Exemplo antigo (ainda disponível para teste)
# --------------------------------------------------------------------
@app.get("/floods/recent", response_class=JSONResponse)
async def floods_recent(hours: int = 24):
    # GeoJSON placeholder: um ponto no centro de SP
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-46.633, -23.550]},
        "properties": {
            "source": "placeholder",
            "event_type": "alagamento",
            "occurrence_ts": datetime.datetime.utcnow().isoformat() + "Z",
            "severity": "desconhecida",
        },
    }
    return {"type": "FeatureCollection", "features": [feature]}


# --------------------------------------------------------------------
# GeoSampa (filtrado e ordenado no servidor)
# --------------------------------------------------------------------
@app.get("/floods/geosampa", response_class=JSONResponse)
async def floods_geosampa(limit: int = 200, days: int = 90):
    """
    Retorna até `limit` pontos mais recentes (ordenados por data desc)
    dentro dos últimos `days` dias. Use days=0 para não filtrar por data.
    """
    data = await merged_floods_geojson()
    feats = data.get("features", []) or []

    def parse_date(props: dict):
        # tenta vários campos comuns nas camadas do GeoSampa
        for k in ("dt_ocorrencia", "dt_carga", "data", "timestamp"):
            v = props.get(k)
            if isinstance(v, str):
                try:
                    # normaliza '2025-09-22Z' -> fromisoformat aceita sem 'Z'
                    return datetime.datetime.fromisoformat(v.replace("Z", ""))
                except Exception:
                    pass
        return None

    cutoff = None if days <= 0 else (datetime.datetime.utcnow() - datetime.timedelta(days=days))

    # pontua features com a melhor data disponível
    scored = []
    for f in feats:
        p = f.get("properties") or {}
        d = parse_date(p)
        if cutoff and d and d < cutoff:
            continue
        scored.append((d or datetime.datetime.min, f))

    # ordena por data decrescente e limita
    scored.sort(key=lambda t: t[0], reverse=True)
    limited = [f for _, f in scored[: max(1, limit)]]

    return {"type": "FeatureCollection", "features": limited}

