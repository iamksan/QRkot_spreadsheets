from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_project_already_invested,
                                check_project_closed, check_project_exists,
                                check_project_invested_sum,
                                check_project_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud, donation_crud
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.utils import investing

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
) -> CharityProjectDB:
    await check_project_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project,
                                                    session,
                                                    commit=False)
    session.add_all(
        investing(new_project, await donation_crud.get_opened(session))
    )
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_projects(
        session: AsyncSession = Depends(get_async_session),
) -> List[CharityProjectDB]:
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_project(
        project_id: int,
        charity_project: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
) -> CharityProjectDB:
    upd_project = await check_project_exists(project_id, session)
    check_project_closed(upd_project)
    check_project_invested_sum(upd_project, charity_project)
    if charity_project.name is not None:
        await check_project_name_duplicate(charity_project.name, session)
    project = await charity_project_crud.update(
        upd_project, charity_project, session
    )
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
) -> CharityProjectDB:
    project = await charity_project_crud.get(project_id, session)
    check_project_already_invested(project)
    return await charity_project_crud.remove(project, session)
