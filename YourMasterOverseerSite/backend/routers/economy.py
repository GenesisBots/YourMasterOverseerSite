
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/economy",
    tags=["economy"]
)

@router.get("/")
def economy_root():
    return {"status": "ok", "message": "economy endpoint alive"}
