from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from sqlalchemy.orm import selectinload, joinedload
from fastapi.responses import StreamingResponse
from app.database import get_session
from app.models.user import User, UserRole
from app.schemas.user import UserRead, UserBase
from app.auth.dependencies import get_current_user
from app.auth.security import get_password_hash
from typing import Optional, List
import pandas as pd
from io import BytesIO
import uuid
import os
import shutil


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
    role: UserRole = Form(UserRole.guest),
    avatar: Optional[bytes] = Form(None),
    session: AsyncSession = Depends(get_session),
    creator: User = Depends(get_current_user)
):
    if creator.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create users")

    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    if role == UserRole.superuser:
        result_superuser = await session.execute(select(User).where(User.role == UserRole.superuser))
        superuser_exists = result_superuser.scalar_one_or_none()
        if superuser_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Superuser already exists")

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
        role=role,
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
    roles: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to search users")

    query = select(User)

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

    if roles:
        roles_list = [role.strip() for role in roles.split(",")]
        query = query.filter(User.role.in_(roles_list))

    result = await session.execute(query)
    users = result.scalars().all()
    return users


@router.get("/get-user/{user_id}", response_model=UserRead)
async def read_user(user_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.role != UserRole.superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/update-user/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_update: UserBase, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.role != UserRole.superuser and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.email:
        user.email = user_update.email
    user.name = user_update.name
    user.surname = user_update.surname

    if current_user.role == UserRole.superuser and user_update.role:
        if user_update.role == UserRole.superuser:
            result_superuser = await session.execute(select(User).where(User.role == UserRole.superuser))
            existing_superuser = result_superuser.scalar_one_or_none()
            if existing_superuser and existing_superuser.id != user_id:
                raise HTTPException(status_code=400, detail="Superuser already exists")
        user.role = user_update.role

    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.patch("/activete/{user_id}", response_model=UserRead)
async def activate_user(user_id: int, activate: bool, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
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
async def delete_user(user_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
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
    roles: Optional[str] = Form(None),
    filename: Optional[str] = Form("users.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = select(User)

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
    if roles:
        roles_list = [role.strip() for role in roles.split(",")]
        query = query.filter(User.role.in_(roles_list))

    result = await session.execute(query)
    users = result.scalars().all()

    data = []
    for user in users:
        data.append({
            "ID": user.id,
            "Email": user.email,
            "Name": user.name,
            "Surname": user.surname,
            "Role": user.role,
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
