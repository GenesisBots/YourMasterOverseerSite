from fastapi import APIRouter
from pydantic import BaseModel
import time

# -----------------------------
# Simulated wallet state
# -----------------------------
WALLET_STATE = {
    "address": "SIMULATED-USER-ADDR",
    "gc_balance": 1000.0,
    "tx_history": []
}

router = APIRouter(
    prefix="/api/wallet",
    tags=["wallet"]
)

# -----------------------------
# MODELS
# -----------------------------
class PaymentRequest(BaseModel):
    amount: float
    receiver: str


# -----------------------------
# ENDPOINT: ROOT
# -----------------------------
@router.get("/")
def wallet_root():
    return {"status": "ok", "message": "wallet endpoint alive"}


# -----------------------------
# ENDPOINT: BALANCE
# -----------------------------
@router.get("/balance")
def get_balance():
    return {
        "address": WALLET_STATE["address"],
        "gc_balance": WALLET_STATE["gc_balance"]
    }


# -----------------------------
# ENDPOINT: TX HISTORY
# -----------------------------
@router.get("/transactions")
def get_transactions():
    return WALLET_STATE["tx_history"]


# -----------------------------
# ENDPOINT: SIMULATED PAYMENT
# -----------------------------
@router.post("/pay")
def simulate_payment(req: PaymentRequest):

    if req.amount <= 0:
        return {"error": "Amount must be positive."}

    if WALLET_STATE["gc_balance"] < req.amount:
        return {"error": "Insufficient balance."}

    # Simulated txid
    txid = f"SIM-TX-{int(time.time())}"

    # Update offline wallet state
    WALLET_STATE["gc_balance"] -= req.amount
    WALLET_STATE["tx_history"].append({
        "txid": txid,
        "amount": req.amount,
        "receiver": req.receiver,
        "timestamp": int(time.time())
    })

    return {
        "status": "ok",
        "txid": txid,
        "new_balance": WALLET_STATE["gc_balance"]
    }
