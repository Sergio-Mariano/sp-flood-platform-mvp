# SP Flood Platform — Quickstart

## Pré-requisitos
- Docker & Docker Compose
- Python 3.11+ (opcional, se quiser rodar localmente)

## Rodando (dev)
```bash
cd docker
docker compose up
# acesse http://localhost:8000
```

## Estrutura
- `backend/app/main.py` — FastAPI + páginas Jinja/Leaflet
- `/floods/recent` — retorna GeoJSON (placeholder, pronto para ligar ao ETL)
- Banco PostGIS já sobe (sem schema ainda)

# Enchentes SP — MVP (FastAPI + Leaflet)

Plataforma MVP para visualizar **ocorrências de alagamento** na cidade de São Paulo usando dados do **GeoSampa**.

- Backend: **FastAPI**
- Frontend: **Leaflet (HTML simples)**
- Execução: **Docker (1 comando)** ou **Python 3.12+** (sem Docker)
- Endpoints principais:
  - `GET /mapa` — página do mapa
  - `GET /floods/geosampa?limit=200&days=90` — GeoJSON (200 pontos mais recentes / 90 dias)

## Rodar com Docker (recomendado)

> Requer Docker Desktop (Windows/macOS) ou Docker Engine (Linux)

```bash
git clone https://github.com/Sergio-Mariano/sp-flood-platform-mvp.git
cd sp-flood-platform-mvp/docker
docker compose up
