from fastapi import APIRouter, status

from src.service.data_base.actions import create_secret_string
from src.shemas.requests import CreateString
from src.shemas.response import CreatedSecretStringResponse

router = APIRouter()


@router.post("/create_string", response_model=CreatedSecretStringResponse, status_code=status.HTTP_201_CREATED)
async def create_string(data: CreateString):
    secret_str = await create_secret_string(**data.model_dump())
    return  {
        "message": "Secret string created successfully",
        "data":  secret_str
    }