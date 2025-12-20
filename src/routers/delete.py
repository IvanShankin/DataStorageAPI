from fastapi import APIRouter, status, BackgroundTasks

from src.exceptions.server_exceptions import SecretNoContent
from src.service.data_base.actions import mark_is_delete_secret, purge_secret_db
from src.schemas.response import BaseResponseModel
from src.service.filesystem.actions import delete_file_safe

router = APIRouter()


@router.delete(
    "/secrets/{name}",
    response_model=BaseResponseModel,
    status_code=status.HTTP_200_OK
)
async def mark_delete_secret(name: str):
    """
    Возвращает 204 если секрет не найден
    """
    result = await mark_is_delete_secret(name)

    if result:
        return BaseResponseModel(message="Secret deleted")
    else:
        raise SecretNoContent(name)


@router.delete(
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