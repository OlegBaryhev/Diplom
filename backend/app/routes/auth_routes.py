from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models.user import User
from app.models.roles import Role
from app.schemas.user import UserRead, UserLogin
from app.auth.security import verify_password, create_access_token, get_password_hash
from app.auth.dependencies import get_current_user
from typing import Optional
import uuid
import os
import shutil

router = APIRouter()

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(User).where(User.email == form_data.username).options(selectinload(User.role_obj))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login_json(login_data: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).where(User.email == login_data.email).options(selectinload(User.role_obj))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    permissions = current_user.role_obj.permissions if current_user.role_obj else None
    user_data = UserRead(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        surname=current_user.surname,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        role_id=current_user.role_id,
        role_name=current_user.role_obj.name if current_user.role_obj else None,
        permissions=permissions,
    )
    return user_data


class UserEditRequest(BaseModel):
    email: str
    name: Optional[str] = None
    surname: Optional[str] = None


@router.put("/edit", response_model=UserRead)
async def edit_me(
    user_data: UserEditRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if user_data.email:
        existing = await session.execute(
            select(User).where(User.email == user_data.email, User.id != current_user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User with this email already exists")
        current_user.email = user_data.email
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.surname is not None:
        current_user.surname = user_data.surname
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        surname=current_user.surname,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        role_id=current_user.role_id,
        role_name=current_user.role_obj.name if current_user.role_obj else None,
        permissions=current_user.role_obj.permissions if current_user.role_obj else None,
    )

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    email: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    password: str = Form(...),
    avatar: UploadFile | None = File(default=None),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    guest_role_result = await session.execute(select(Role).where(Role.name == "guest"))
    guest_role = guest_role_result.scalar_one_or_none()
    if not guest_role:
        raise HTTPException(status_code=500, detail="Guest role not found in database")

    hashed_password = get_password_hash(password)
    avatar_url = None
    if avatar:
        file_extension = avatar.filename.split(".")[-1] if avatar.filename else "png"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        avatar_path = os.path.join("avatars", unique_filename)
        os.makedirs("avatars", exist_ok=True)
        with open(avatar_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        avatar_url = f"/avatars/{unique_filename}"

    db_user = User(
        email=email,
        name=name,
        surname=surname,
        hashed_password=hashed_password,
        role_id=guest_role.id,
        avatar_url=avatar_url,
        is_active=1
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.post("/upload-avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    ext = avatar.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "png"
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join("avatars", filename)
    os.makedirs("avatars", exist_ok=True)

    contents = await avatar.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    avatar_url = f"/avatars/{filename}"
    current_user.avatar_url = avatar_url
    session.add(current_user)
    await session.commit()
    
    return {"avatar_url": avatar_url}