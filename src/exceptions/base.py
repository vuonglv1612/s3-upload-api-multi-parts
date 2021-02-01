from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional, Any, Dict


class NotFoundException(HTTPException):
    def __init__(self, detail: Any, headers: Optional[Dict[str, Any]]) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class BadRequestException(HTTPException):
    def __init__(self, detail: Any, headers: Optional[Dict[str, Any]]) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
        )
