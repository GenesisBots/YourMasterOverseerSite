import os
import subprocess

# ============================
# 1. Install Dependencies
# ============================
print("Installing FastAPI and Uvicorn...")
subprocess.run(["pip", "install", "fastapi", "uvicorn"], check=True)

# ============================
# 2. Create Folder Structure
# ============================
base_path = os.path.join(os.getcwd(), "backend")
routers_path = os.path.join(base_path, "routers")

os.makedirs(routers_path, exist_ok=True)

print(f"Backend folder created at: {base_path}")

# ============================
# 3. Create main.py
# ============================
main_py = f"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import bots, battle, evolution, marketplace, economy, user, wallet

app = FastAPI()

# CORS for localhost + future cloud deployment
origins = [
    "http://localhost:8000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost",
    "https://yourmasteroverseer.com",
    "http://yourmasteroverseer.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(bots.router)
app.include_router(battle.router)
app.include_router(evolution.router)
app.include_router(marketplace.router)
app.include_router(economy.router)
app.include_router(user.router)
app.include_router(wallet.router)

@app.get("/")
def root():
    return {{"status": "ok", "message": "Backend is running"}}
"""

with open(os.path.join(base_path, "main.py"), "w") as f:
    f.write(main_py)

# ============================
# 4. Create Router Templates
# ============================
router_template = lambda name: f"""
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/{name}",
    tags=["{name}"]
)

@router.get("/")
def {name}_root():
    return {{"status": "ok", "message": "{name} endpoint alive"}}
"""

router_files = [
    "bots",
    "battle",
    "evolution",
    "marketplace",
    "economy",
    "user",
    "wallet"
]

for r in router_files:
    with open(os.path.join(routers_path, f"{r}.py"), "w") as f:
        f.write(router_template(r))

print("All router files created.")

# ============================
# 5. Done
# ============================
print("\nBackend skeleton successfully generated!")
print("To run your backend:")
print("  cd backend")
print("  uvicorn main:app --reload")
