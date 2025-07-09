from fastapi import FastAPI
from database import init_db

app=FastAPI(title="User Service")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def health_check():
    return {"status":"User service runnng"}

