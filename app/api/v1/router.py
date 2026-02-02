from fastapi import APIRouter
from app.api.v1.routes.items import router as items_router

router = APIRouter()
router.include_router(items_router, prefix="/items", tags=["items"])
