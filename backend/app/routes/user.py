from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from fastapi.responses import StreamingResponse
from app.database import get_session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserRead, UserBase
from app.auth.dependencies import get_current_user, has_permission
from app.auth.security import get_password_hash
from typing import Optional
import pandas as pd
from io import BytesIO
import uuid
import os

router = APIRouter()

@router.get("/list-simplified/", response_model=list[dict])
async def get_users_simple(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(select(User))
    users = result.scalars().all()
    simplified_users = [
        {"value": user.id, "name": f"{user.name} {user.surname}"}
        for user in users
    ]
    return simplified_users

@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    email: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    password: str = Form(...),
    role_id: Optional[int] = Form(None),
    avatar: Optional[bytes] = Form(None),
    session: AsyncSession = Depends(get_session),
    creator: User = Depends(has_permission("users_control", "write"))
):
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    if role_id:
        role_result = await session.execute(select(Role).where(Role.id == role_id))
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role_id")

    hashed_password = get_password_hash(password)
    avatar_url = None
    if avatar:
        file_extension = "png"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        avatar_path = os.path.join("avatars", unique_filename)
        os.makedirs("avatars", exist_ok=True)
        with open(avatar_path, "wb") as buffer:
            buffer.write(avatar)
        avatar_url = f"/avatars/{unique_filename}"

    db_user = User(
        email=email,
        name=name,
        surname=surname,
        hashed_password=hashed_password,
        role_id=role_id,
        avatar_url=avatar_url,
        is_active=1
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.post("/search", response_model=list[UserRead])
async def search_users(
    search: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    role_ids: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("users_control", "read"))
):
    query = select(User).options(selectinload(User.role_obj))

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.surname.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if is_active is not None:
        query = query.filter(User.is_active == (1 if is_active else 0))

    if role_ids:
        ids_list = [int(rid.strip()) for rid in role_ids.split(",") if rid.strip().isdigit()]
        if ids_list:
            query = query.filter(User.role_id.in_(ids_list))

    result = await session.execute(query)
    users = result.scalars().all()
    return users

@router.get("/get-user/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if not (current_user.role_obj and current_user.role_obj.name == "superuser") and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    result = await session.execute(select(User).where(User.id == user_id).options(selectinload(User.role_obj)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/update-user/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserBase,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if not (current_user.role_obj and current_user.role_obj.name == "superuser") and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.email:
        user.email = user_update.email
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.surname is not None:
        user.surname = user_update.surname

    if user_update.role_id is not None and current_user.role_obj and current_user.role_obj.has_permission("users_control", "change-role"):
        role_result = await session.execute(select(Role).where(Role.id == user_update.role_id))
        new_role = role_result.scalar_one_or_none()
        if not new_role:
            raise HTTPException(status_code=400, detail="Invalid role_id")
        user.role_id = new_role.id

    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.patch("/activate/{user_id}", response_model=UserRead)
async def activate_user(
    user_id: int,
    activate: bool,
    current_user: User = Depends(has_permission("users_control", "status")),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = 1 if activate else 0
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(has_permission("users_control", "delete")),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()
    return

@router.post("/export/xlsx")
async def export_users_xlsx(
    search: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    role_ids: Optional[str] = Form(None),
    filename: Optional[str] = Form("users.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("users_control", "download")),
):
    query = select(User).options(selectinload(User.role_obj))

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.surname.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )
    if is_active is not None:
        query = query.filter(User.is_active == (1 if is_active else 0))
    if role_ids:
        ids_list = [int(rid.strip()) for rid in role_ids.split(",") if rid.strip().isdigit()]
        if ids_list:
            query = query.filter(User.role_id.in_(ids_list))

    result = await session.execute(query)
    users = result.scalars().all()

    data = []
    for user in users:
        data.append({
            "ID": user.id,
            "Email": user.email,
            "Name": user.name,
            "Surname": user.surname,
            "Role": user.role_obj.name if user.role_obj else None,
            "Is Active": bool(user.is_active),
            "Avatar URL": user.avatar_url,
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Users")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )