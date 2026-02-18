from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from datetime import datetime

from src.db.database import get_session
from src.services.parking_services import parking_service
from src.db.accessor.schemas.parkinglot import (
    ParkingLotCreate,
    ParkingLotResponse,
)

from src.api.v1.dependencies import get_current_user
from src.db.models.user import User

router = APIRouter(prefix="/lots", tags=["ParkingLots"])

@router.post(
    "/create",
    response_model=ParkingLotResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_parking_lot(
    data: ParkingLotCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create parking lots"
        )

    parking_lot = await parking_service.create_parking_lot(
        parking_data=data,
        admin_id=current_user.uid,
        session=session
    )
    return parking_lot

@router.get("", response_model=list[ParkingLotResponse])
async def get_all_parking_lots(
    session: AsyncSession = Depends(get_session),
    current_user:User =Depends(get_current_user)
):
    return await parking_service.get_all_parking_lots(session)


@router.get("/search", response_model=list[ParkingLotResponse])
async def search_parking_lots(
        q: str = Query(..., min_length=1),
        session: AsyncSession = Depends(get_session),
        current_user:User=Depends(get_current_user)
    ):
        q = q.strip()
        return await parking_service.search_parking_lots(q, session)


@router.get("/{parking_lot_uid}/slots")
async def get_parking_lot_slots(
        parking_lot_uid: UUID,
        session: AsyncSession = Depends(get_session),
        current_user:User=Depends(get_current_user)
    ):
        return await parking_service.get_slots_by_parking_lot(
            parking_lot_uid,
            session
        )
@router.get("/{parking_lot_uid}/available-slots")
async def get_available_slots(
        parking_lot_uid: UUID,
        start_time: datetime,
        end_time: datetime,
        session: AsyncSession = Depends(get_session),
        current_user:User=Depends(get_current_user)
    ):
        return await parking_service.get_available_slots(
            parking_lot_uid,
            start_time,
            end_time,
            session
        )
