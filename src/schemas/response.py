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