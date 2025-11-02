# Backend — Enchentes SP (FastAPI)

API em **FastAPI** que expõe dados de alagamentos de São Paulo e serve a página do mapa (Leaflet).

## Requisitos
- Python **3.12+**
- `pip` atualizado
- (Opcional) Docker, se preferir rodar tudo em contêiner

---

## Como rodar local (sem Docker)

```bash
# dentro da pasta backend/
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# instalar o pacote do backend e deps principais
pip install -e .
pip install "uvicorn[standard]" fastapi httpx "psycopg[binary]" jinja2 python-multipart apscheduler

# subir a API com reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
