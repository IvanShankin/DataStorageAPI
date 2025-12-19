from fastapi import APIRouter, status

from src.service.data_base.actions import create_secret_string, create_next_string_version
from src.schemas.requests import SecretStringCreate
from src.schemas.response import SecretStringResponse, CreatedSecretStringData

router = APIRouter()


@router.post("/secrets_strings/create_string", response_model=SecretStringResponse, status_code=status.HTTP_201_CREATED)
async def create_string(data: SecretStringCreate):
    secret_str = await create_secret_string(**data.model_dump())
    return SecretStringResponse(
        message="Secret string created successfully",
        data=CreatedSecretStringData(name=data.name, **(secret_str.to_dict()))
    )


@router.post(
    "/secrets_strings/versions",
    response_model=SecretStringResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_next_secret_version(data: SecretStringCreate):
    secret_str = await create_next_string_version(data)
    return SecretStringResponse(
        message="Secret string version created successfully",
        data=CreatedSecretStringData(name=data.name, **(secret_str.to_dict()))
    )
