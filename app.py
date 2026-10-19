from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from metrics import load_store, compute_metrics

app = FastAPI()

DATA_DIR = Path(__file__).parent / "Data"
STORES = {p.name: load_store(p) for p in sorted(DATA_DIR.glob("STORE*"))}
METRICS = {name: compute_metrics(data) for name, data in STORES.items()}

@app.get('/stores')
def list_stores():
    return list(STORES)

@app.get("/stores/{name}/metrics")
def get_metrics(name: str):
    if name not in METRICS:
        raise HTTPException(status_code=404, detail=f"Store {name} not found")
    return METRICS[name]

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")