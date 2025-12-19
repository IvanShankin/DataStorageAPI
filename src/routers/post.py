from fastapi import APIRouter, status, BackgroundTasks

from src.service.data_base.actions import create_secret_string, create_next_string_version, purge_secret_db
from src.schemas.requests import SecretStringCreate
from src.schemas.response import SecretStringResponse, CreatedSecretStringData, BaseResponseModel
from src.service.filesystem.actions import delete_file_safe

router = APIRouter()


@router.post(
    "/secrets_strings/create_string",
    response_model=SecretStringResponse,
    status_code=status.HTTP_201_CREATED
)
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


@router.post(
    "/secrets/{name}/purge",
    response_model=BaseResponseModel,
    status_code=status.HTTP_202_ACCEPTED,
)
async def purge_secret(
    name: str,
    background_tasks: BackgroundTasks
):
    file_paths = await purge_secret_db(name)
    for path in file_paths:
        background_tasks.add_task(delete_file_safe, path)

    return BaseResponseModel(message="Secret purge")
