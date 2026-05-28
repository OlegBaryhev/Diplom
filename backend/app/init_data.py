import random
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Category, Product, Brand, Analog, User
from app.models.roles import Role
from app.models.logs.log_models import LogSettings
from app.database import SessionLocal
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.auth.permissions_data import SUPERUSER_PERMISSIONS, MODERATOR_PERMISSIONS, GUEST_PERMISSIONS

load_dotenv("security.env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_data():
    async with SessionLocal() as session:
        result = await session.execute(select(Role))
        existing_roles = {role.name: role for role in result.scalars().all()}

        if "superuser" not in existing_roles:
            superuser_role = Role(name="superuser", permissions=SUPERUSER_PERMISSIONS)
            session.add(superuser_role)
        else:
            superuser_role = existing_roles["superuser"]

        if "moderator" not in existing_roles:
            moderator_role = Role(name="moderator", permissions=MODERATOR_PERMISSIONS)
            session.add(moderator_role)
        else:
            moderator_role = existing_roles["moderator"]

        if "guest" not in existing_roles:
            guest_role = Role(name="guest", permissions=GUEST_PERMISSIONS)
            session.add(guest_role)
        else:
            guest_role = existing_roles["guest"]

        await session.commit()

        result = await session.execute(select(Role))
        roles = {role.name: role for role in result.scalars().all()}
        superuser_role = roles["superuser"]
        moderator_role = roles["moderator"]
        guest_role = roles["guest"]

        default_log_settings = [
            ("user", 30, 5),
            ("category", 30, 5),
            ("brand", 30, 5),
            ("order", 30, 5),
            ("product", 30, 5),
        ]
        for table_name, time_min, count_limit in default_log_settings:
            existing_setting = await session.execute(
                select(LogSettings).where(LogSettings.table_name == table_name)
            )
            if not existing_setting.scalar_one_or_none():
                session.add(LogSettings(
                    table_name=table_name,
                    time_retention_minutes=time_min,
                    count_retention_limit=count_limit
                ))
        await session.commit()

        result = await session.execute(select(Category))
        categories = result.scalars().all()
        if not categories:
            categories = []
            for i in range(1, 11):
                c = Category(name=f"Категория_{i}", description=f"Описание {i}")
                session.add(c)
                categories.append(c)
            await session.commit()
            result = await session.execute(select(Category))
            categories = result.scalars().all()

        result_brand = await session.execute(select(Brand))
        brands = result_brand.scalars().all()
        if not brands:
            brands = []
            for i in range(1, 11):
                b = Brand(name=f"Бренд_{i}", description=f"Описание бренда {i}")
                session.add(b)
                brands.append(b)
            await session.commit()
            result_brand = await session.execute(select(Brand))
            brands = result_brand.scalars().all()

        result = await session.execute(select(Product))
        products = result.scalars().all()
        if not products:
            for i in range(1, 301):
                price = random.randint(50000, 1500000)
                category = random.choice(categories)
                brand = random.choice(brands)
                discount = random.choice([0, random.randint(5, 50)])
                product = Product(
                    name=f"Продукт_{i}",
                    description=f"Описание продукта {i}",
                    price=price,
                    discount=discount,
                    category_id=category.id,
                    brand_id=brand.id
                )
                session.add(product)
            await session.commit()

        result_analogs = await session.execute(select(Analog))
        analogs = result_analogs.scalars().all()
        if not analogs:
            for i in range(1, 11):
                price = random.randint(50000, 1500000)
                category = random.choice(categories)
                brand = random.choice(brands)
                analog = Analog(
                    name=f"Аналог_продукта_{i}",
                    description=f"Описание аналога продукта {i}",
                    price=price,
                    category_id=category.id,
                    brand_id=brand.id
                )
                session.add(analog)
            await session.commit()

        admin_email = os.getenv("ADMIN_LOGIN")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_password:
            raise ValueError("ADMIN_PASSWORD not set in security.env")
        existing_admin = await session.execute(select(User).where(User.email == admin_email))
        admin_user = existing_admin.scalars().first()
        if not admin_user:
            hashed_password = pwd_context.hash(admin_password)
            admin_user = User(
                name="Админ",
                surname="Админович",
                email=admin_email,
                hashed_password=hashed_password,
                role_id=superuser_role.id,
                is_active=1,
            )
            session.add(admin_user)
            await session.commit()