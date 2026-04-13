
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)

@router.get("/")
def user_root():
    return {"status": "ok", "message": "user endpoint alive"}
