from fastapi import HTTPException, status

class NameAlreadyExists(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Name '{name}' already exists"
        )

class SecretNotFound(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Name '{name}' not found"
        )