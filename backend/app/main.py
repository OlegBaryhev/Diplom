from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from app.routes import products, category, cart, order, auth_routes, brand, user, analogs, recalculate, recalculate_history, roles
from app.routes.logs import router as logs_router
from app.database import create_tables, init_logs
from app.init_data import init_data
from app.core.log_cleanup import start_log_cleanup_scheduler
import asyncio
import logging
import os

app = FastAPI(
    title="Diplom API",
    description="API for products",
    version="0.1.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(category.router, prefix="/category", tags=["Category"])
app.include_router(brand.router, prefix="/brand", tags=["Brand"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(order.router, prefix="/order", tags=["Order"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(analogs.router, prefix="/analogs", tags=["Analogs"])
app.include_router(recalculate.router, prefix="/recalculate", tags=["Recalculate"])
app.include_router(recalculate_history.router, prefix="/recalculate_history", tags=["RecalculateHistory"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])

os.makedirs("avatars", exist_ok=True)
app.mount("/avatars", StaticFiles(directory="avatars"), name="avatars")

os.makedirs("product_images", exist_ok=True)
app.mount("/product_images", StaticFiles(directory="product_images"), name="product_images")

logger = logging.getLogger("uvicorn.error")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.error(f"Validation error: {exc.errors()} Body: {body.decode('utf-8')}")
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.on_event("startup")
async def startup():
    await create_tables()
    await init_logs()
    await init_data()
    asyncio.create_task(start_log_cleanup_scheduler(interval_minutes=5))