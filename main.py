"""FastAPI application exposing signup, login, refresh, view, and logout APIs."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mongodb.indexes import init_indexes
from api.admin_auth import router as sadmin_auth_router
from api.super_admin_auth import router as auth_router
from api.admin.router import router as admin_view_router
from api.super_admin.router import router as sadmin_view_router
from api.user.router import router as user_view_router
from api.announcement.router import router as announcement_router
from redis_db.redis_instance import redis

from fastapi.middleware.cors import CORSMiddleware

from security.google_sheet import initialize_google_sheet

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await init_indexes()
    
    await initialize_google_sheet()

    yield


app = FastAPI(lifespan=lifespan)

# Add CORS Middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dextro-sage-website.vercel.app","http://localhost:5173", "http://127.0.0.1:5173","https://dextro-sage-website-2vpm6brpb-vikrant5.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(sadmin_auth_router)

app.include_router(sadmin_view_router)

app.include_router(admin_view_router)

app.include_router(user_view_router)

app.include_router(announcement_router)
