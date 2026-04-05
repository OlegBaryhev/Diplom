from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.user import User
from sqlalchemy.future import select
from app.auth.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
) -> User:
    crendentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise crendentials_exception

        try:
            user_id = int(user_id_str) 
        except ValueError:
            raise crendentials_exception

    except JWTError:
        raise crendentials_exception

    resualt = await session.execute(select(User).where(User.id == user_id))
    user = resualt.scalar_one_or_none()

    if user is None:
        raise crendentials_exception

    return user