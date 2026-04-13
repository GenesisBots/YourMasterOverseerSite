
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/evolution",
    tags=["evolution"]
)

@router.get("/")
def evolution_root():
    return {"status": "ok", "message": "evolution endpoint alive"}
