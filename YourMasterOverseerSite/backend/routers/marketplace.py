
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/marketplace",
    tags=["marketplace"]
)

@router.get("/")
def marketplace_root():
    return {"status": "ok", "message": "marketplace endpoint alive"}
