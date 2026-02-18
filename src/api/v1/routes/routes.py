from fastapi import APIRouter
from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.parkinglot import router as parkinglot_router



router = APIRouter()
router.include_router(auth_router)
router.include_router(parkinglot_router)