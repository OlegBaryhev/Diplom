from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_session
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user
from app.schemas.user import UserRead
from app.auth.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr
import shutil
import os
import uuid

router = APIRouter()

@router.post("/register", response_model=UserRead)
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

    new_role = UserRole.guest

    hashed_password = get_password_hash(password)
    avatar_url = None
    if avatar:
        file_extension = avatar.filename.split(".")[-1]
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
        role=new_role,
        avatar_url=avatar_url
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

class UserEditRequest(BaseModel):
    name: str
    surname: str
    email: EmailStr

@router.put("/edit", response_model=UserRead)
async def edit_user(
    user_edit: UserEditRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Проверка, не занят ли новый email
    if user_edit.email != current_user.email:
        result = await session.execute(select(User).where(User.email == user_edit.email))
        user_with_email = result.scalar_one_or_none()
        if user_with_email:
            raise HTTPException(status_code=400, detail="User with this email already exists")

    # Обновление полей
    current_user.name = user_edit.name
    current_user.surname = user_edit.surname
    current_user.email = user_edit.email

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user