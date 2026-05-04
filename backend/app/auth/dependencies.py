from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_session
from app.models.user import User
from app.auth.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await session.execute(
        select(User).where(User.id == user_id).options(selectinload(User.role))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def has_permission(section: str, action: str):
    async def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role is None:
            default_perms = {
                "home": {"all_subsections": ["read"]},
                "products": {"all_subsections": ["read", "buy"]}
            }
            if default_perms.get(section, {}).get("all_subsections", []).count(action):
                return True
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        if current_user.role.has_permission(section, action):
            return True
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return dependency