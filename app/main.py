import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base, SessionLocal
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers import profile
from app.routers.address import router as address_router
from app.routers.book import router as book_router
from app.routers import cart
from app.routers import order
from app.routers import admin_order
from app.routers.plan import router as plan_router
from app.services.plan_service import check_and_expire_plans

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Base.metadata.create_all skipped/deferred: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield



app = FastAPI(
    title="words-traffic API",
    description="Backend API for words-traffic online bookstore where customers can purchase books and receive home delivery.",
    version="1.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(profile.router)
app.include_router(address_router)
app.include_router(book_router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(admin_order.router)
app.include_router(plan_router)
