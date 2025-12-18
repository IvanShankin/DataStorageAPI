from fastapi import APIRouter
from src.requests.get import router as get_router
from src.requests.post import router as post_router

main_router = APIRouter()
main_router.include_router(get_router)
main_router.include_router(post_router)