from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models.roles import Role
from app.schemas.roles import RoleRead
from app.auth.dependencies import has_permission
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=list[RoleRead])
async def get_roles(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("users_control", "read"))
):
    result = await session.execute(select(Role))
    roles = result.scalars().all()
    return roles