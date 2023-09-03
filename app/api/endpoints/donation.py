from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charity_project_crud, donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationResponse
from app.utils.investing import investing

router = APIRouter()


@router.post(
    '/',
    response_model=DonationResponse,
    dependencies=[Depends(current_user)],
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
) -> DonationResponse:
    new_donation = await donation_crud.create(donation,
                                              session,
                                              user,
                                              commit=False)
    session.add_all(
        investing(new_donation, await charity_project_crud.get_opened(session))
    )
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=List[DonationDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=List[DonationResponse],
    response_model_exclude_none=True,
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
) -> DonationResponse:
    return await donation_crud.get_by_user(user, session)
