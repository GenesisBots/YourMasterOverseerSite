from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS MUST be before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow everything for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers inside /routers
from routers import bots, battle, evolution, marketplace, economy, user, wallet

app.include_router(bots.router)
app.include_router(battle.router)
app.include_router(evolution.router)
app.include_router(marketplace.router)
app.include_router(economy.router)
app.include_router(user.router)
app.include_router(wallet.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running"}
