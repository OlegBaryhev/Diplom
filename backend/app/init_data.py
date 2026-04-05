import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Category, Product, Brand, Analog, User
from app.database import SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_data():
    async with SessionLocal() as session:
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

        result = await session.execute(select(Product))
        products = result.scalars().all()

        result_brand = await session.execute(select(Brand))
        brands = result_brand.scalars().all()

        if not brands:
            brands = []
            for i in range(1, 11):
                b = Brand(
                    name=f"Бренд_{i}",
                    description=f"Описание бренда {i}"
                )
                session.add(b)
                brands.append(b)
            await session.commit()

        if not products:
            for i in range(1, 11):
                price = random.randint(50000, 1500000)
                category = random.choice(categories)
                brand = random.choice(brands)
                product = Product(
                    name=f"Продукт_{i}",
                    description=f"Описание продукта {i}",
                    price=price,
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

        admin_email = "administrator@gmail.com"
        existing_admin = await session.execute(select(User).where(User.email == admin_email))
        admin_user = existing_admin.scalars().first()

        if not admin_user:
            hashed_password = pwd_context.hash("admin123")
            admin_user = User(
                name="Админ",
                surname="Админович",
                email=admin_email,
                hashed_password=hashed_password,
                role="superuser",
                is_active=1,
            )
            session.add(admin_user)
            await session.commit()
