from fastapi import APIRouter, status

from src.service.data_base.actions import mark_is_delete_secret
from src.schemas.response import BaseResponseModel

router = APIRouter()


@router.delete(
    "/secrets/{name}",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK
)
async def mark_delete_secret(name: str):
    await mark_is_delete_secret(name)
    return BaseResponseModel(message="Secret deleted")
