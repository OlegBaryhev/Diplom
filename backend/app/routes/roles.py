from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, asc, desc, func
from typing import Optional, List
from app.database import get_session
from app.models.roles import Role
from app.models.user import User
from app.schemas.roles import RoleRead, RoleCreate, RoleUpdate
from app.schemas.paginated import PaginatedResponse
from app.auth.dependencies import get_current_user

router = APIRouter()

async def is_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.role_obj or current_user.role_obj.name != "superuser":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superuser can manage roles")
    return current_user

@router.get("/", response_model=list[RoleRead])
async def get_roles(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    result = await session.execute(select(Role).order_by(Role.id))
    roles = result.scalars().all()
    return roles

@router.post("/search", response_model=PaginatedResponse[RoleRead])
async def search_roles(
    search: Optional[str] = Form(None),
    sort_by: Optional[str] = Form("id_asc"),
    page: int = Form(1),
    page_size: int = Form(100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    count_query = select(func.count(Role.id))
    if search:
        count_query = count_query.where(Role.name.ilike(f"%{search}%"))
    total = (await session.execute(count_query)).scalar_one()

    query = select(Role)
    if search:
        query = query.filter(Role.name.ilike(f"%{search}%"))
    if sort_by == "name_asc":
        query = query.order_by(asc(Role.name))
    elif sort_by == "name_desc":
        query = query.order_by(desc(Role.name))
    else:
        query = query.order_by(asc(Role.id))

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    return {"items": result.scalars().all(), "total": total}

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    existing = await session.execute(select(Role).where(Role.name == role_data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
    db_role = Role(name=role_data.name, display_name=role_data.display_name, permissions=role_data.permissions)
    session.add(db_role)
    await session.commit()
    await session.refresh(db_role)
    return db_role

@router.get("/{role_id}", response_model=RoleRead)
async def get_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role_update.name is not None:
        role.name = role_update.name
    if role_update.display_name is not None:
        role.display_name = role_update.display_name
    if role_update.permissions is not None:
        role.permissions = role_update.permissions
    await session.commit()
    await session.refresh(role)
    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(is_superuser)
):
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    await session.delete(role)
    await session.commit()
    return