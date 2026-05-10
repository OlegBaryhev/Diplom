from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserRead, UserLogin
from app.auth.security import verify_password, create_access_token
from app.auth.dependencies import get_current_user
from datetime import timedelta

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
    return {"access_token": access_token, "token_type": "bearer"}

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
        permissions=permissions,
    )
    return user_data