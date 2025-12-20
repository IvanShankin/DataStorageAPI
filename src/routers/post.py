from fastapi import APIRouter, status, UploadFile, File, Form

from src.service.data_base.actions import create_secret_string, create_next_string_version,\
    create_secret_file_service, create_next_file_version
from src.schemas.requests import SecretStringCreate
from src.schemas.response import SecretStringResponse, CreatedSecretStringData, SecretFileResponse, \
    CreatedSecretFileData

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
    "/secrets_files/create_files",
    response_model=SecretFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_secret_file(
    name: str = Form(...),
    file: UploadFile = File(...),
    nonce: str = Form(...),
    sha256: str = Form(...),
):
    secret_file = await create_secret_file_service(
        name=name,
        file=file,
        nonce_b64=nonce,
        sha256_b64=sha256,
    )
    return SecretFileResponse(
        message="Secret file created successfully",
        data=CreatedSecretFileData(name=name, file_id=secret_file.file_id)
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
    "/secrets_files/versions",
    response_model=SecretFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_next_secret_version(
    name: str = Form(...),
    file: UploadFile = File(...),
    nonce: str = Form(...),
    sha256: str = Form(...)
):
    secret_file = await create_next_file_version(name=name, file=file, nonce_b64=nonce, sha256_b64=sha256)

    return SecretFileResponse(
        message="Secret string version created successfully",
        data=CreatedSecretFileData(name=name, file_id=secret_file.file_id)
    )

