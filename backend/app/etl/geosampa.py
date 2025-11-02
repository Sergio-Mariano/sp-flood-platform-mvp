# backend/app/etl/geosampa.py
import httpx
import re
from typing import List, Dict

WFS_BASE = "https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows"

async def discover_layers() -> List[str]:
    """
    Busca camadas WFS e filtra nomes que contenham 'alag' ou 'inund'.
    Ex.: 'defesacivil:alagamento_2025'.
    """
    params = {"service": "WFS", "request": "GetCapabilities", "version": "1.1.0"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(WFS_BASE, params=params)
        r.raise_for_status()
        xml = r.text

    names = re.findall(r"<Name>(.*?)</Name>", xml)
    candidates = [n for n in names if re.search(r"alag|inund", n, re.IGNORECASE)]
    # ordena por ano se houver número no nome; mais recentes primeiro
    def year_key(s: str) -> str:
        nums = re.findall(r"\d{4}", s)
        return nums[-1] if nums else "0000"
    candidates.sort(key=year_key, reverse=True)
    return candidates[:4]  # pega as 4 mais prováveis

async def fetch_geojson(type_name: str, max_features: int = 5000) -> Dict:
    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": type_name,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "maxFeatures": str(max_features),
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.get(WFS_BASE, params=params)
        r.raise_for_status()
        return r.json()

async def merged_floods_geojson() -> Dict:
    layers = await discover_layers()
    features = []
    for layer in layers:
        try:
            gj = await fetch_geojson(layer)
            if gj.get("features"):
                features.extend(gj["features"])
        except Exception:
            # Em MVP, se uma camada falhar, seguimos com as demais
            pass
    return {"type": "FeatureCollection", "features": features}
