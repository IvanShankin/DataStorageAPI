from fastapi import HTTPException, status

class NameAlreadyExists(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Name '{name}' already exists"
        )