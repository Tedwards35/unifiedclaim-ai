from fastapi import FastAPI

app = FastAPI(title="UnifiedClaim AI – Day 1")

@app.get("/status")
def status():
    return {"ok": True}
