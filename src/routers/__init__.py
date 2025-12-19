from fastapi import APIRouter
from src.routers.get import router as get_router
from src.routers.post import router as post_router
from src.routers.delete import router as delete_router

main_router = APIRouter()
main_router.include_router(get_router)
main_router.include_router(post_router)
main_router.include_router(delete_router)