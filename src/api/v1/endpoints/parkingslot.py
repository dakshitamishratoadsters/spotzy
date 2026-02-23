from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.database import get_session
from src.api.v1.dependencies import get_current_user
from src.db.models.user import User
from src.services.slots_services import parking_slot_service
from src.db.accessor.schemas.parkingslot import (
    SlotCreate,
    SlotUpdate,
    SlotResponse,
)

router = APIRouter(
    prefix="/parking-slots",
    tags=["Parking Slots"]
)


# ===================== CREATE SLOT (ADMIN ONLY) =====================
@router.post(
    "/{parking_lot_id}",
    response_model=SlotResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_parking_slot(
    parking_lot_id: UUID,
    slot_data: SlotCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        return await parking_slot_service.create_slot(
            parking_lot_id=parking_lot_id,
            slot_data=slot_data,
            session=session,
            current_user=current_user
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===================== GET ALL SLOTS BY PARKING LOT (USER ACCESS) =====================
@router.get(
    "/by-lot/{parking_lot_id}",
    response_model=List[SlotResponse]
)
async def get_slots_by_parking_lot(
    parking_lot_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)  # user or admin
):
    return await parking_slot_service.get_slots_by_parking_lot(
        parking_lot_id=parking_lot_id,
        session=session
    )


# ===================== UPDATE SLOT (ADMIN ONLY) =====================
@router.put(
    "/{slot_id}",
    response_model=SlotResponse
)
async def update_parking_slot(
    slot_id: UUID,
    slot_data: SlotUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        return await parking_slot_service.update_slot(
            slot_id=slot_id,
            slot_data=slot_data,
            session=session,
            current_user=current_user
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))