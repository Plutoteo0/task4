from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from metrics import load_store, compute_metrics
from pydantic import BaseModel
from chat import answer
from filter import filter_users

app = FastAPI()

DATA_DIR = Path(__file__).parent / "Data"
STORES = {p.name: load_store(p) for p in sorted(DATA_DIR.glob("STORE*"))}
METRICS = {name: compute_metrics(data) for name, data in STORES.items()}

class ChatRequest(BaseModel):
    messages: list[dict]

@app.get('/stores')
def list_stores():
    return list(STORES)

@app.get("/stores/{name}/metrics")
def get_metrics(name: str):
    if name not in METRICS:
        raise HTTPException(status_code=404, detail=f"Store {name} not found")
    return METRICS[name]

@app.post("/chat")
def chat(req: ChatRequest):
    return answer(req.messages, METRICS, STORES)

@app.get("/stores/{name}/users")
def get_users(name, email_prefix: str = ""):
    if name not in METRICS:
        raise HTTPException(status_code=404, detail=f"Store {name} not found")
    if not email_prefix:
        return
    prefixes = email_prefix.split(",")
    rows = filter_users(STORES[name]["users"], prefixes)
    return {"count": len(rows), "users": rows[:200]}

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")