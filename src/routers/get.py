from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import FileResponse

from src.config import SECRET_FILES_DIR
from src.schemas.response import FullSecretStringResponse, SecretFileMetaResponse
from src.service.data_base.actions import get_secret_string, get_secret_files, create_log

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get(
    "/secret_string/{name}",
    response_model=FullSecretStringResponse,
    status_code=status.HTTP_200_OK,
)
async def get_secret_string_route(
    name: str,
    version: int | None = None,
):
    secret_str = await get_secret_string(name, version)

    if not secret_str:
        raise HTTPException(status_code=404, detail="Secret string not found")

    await create_log("The user received a secret string", name)

    return FullSecretStringResponse(
        name=name,
        **(secret_str.to_dict())
    )


@router.get(
    "/secrets/files/{name}",
    response_model=SecretFileMetaResponse,
    status_code=status.HTTP_200_OK,
)
async def get_secret_file_meta(
    name: str,
    version: int | None = None,
):
    secret_file = await get_secret_files(name, version)

    if not secret_file:
        raise HTTPException(status_code=404, detail="Secret file not found")

    await create_log("The user received file metadata", name)

    return SecretFileMetaResponse(
        name=name,
        **(secret_file.to_dict())
    )



@router.get(
    "/secrets/files/{name}/download",
    status_code=status.HTTP_200_OK,
)
async def download_secret_file(
    name: str,
    version: int | None = None,
):
    secret_file = await get_secret_files(name, version)

    if not secret_file:
        raise HTTPException(status_code=404, detail="Secret file not found")

    file_path = SECRET_FILES_DIR / secret_file.file_name

    if not file_path.exists():
        raise HTTPException(status_code=410, detail="File missing on disk")

    await create_log("The user received the file", name)

    return FileResponse(
        path=file_path,
        filename=secret_file.file_name,
        media_type="application/octet-stream",
    )
