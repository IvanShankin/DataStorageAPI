from datetime import datetime

from pydantic import BaseModel



class BaseResponseModel(BaseModel):
    message: str


class CreatedSecretStringData(BaseModel):
    string_id: int
    name: str
    enc_version: int

    model_config = {
        "from_attributes": True
    }

class SecretStringResponse(BaseResponseModel):
    data: CreatedSecretStringData


class CreatedSecretFileData(BaseModel):
    file_id: int
    name: str


class SecretFileResponse(BaseResponseModel):
    data: CreatedSecretFileData


class FullSecretStringResponse(CreatedSecretStringData):
    encrypted_data: str
    nonce: str
    sha256: str
    version: int


class SecretFileMetaResponse(BaseModel):
    name: str
    version: int
    file_name: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
