from typing import Any, Dict, Optional

from src.exceptions.base import BadRequestException


class IllegalNameException(BadRequestException):
    def __init__(
        self, name: str, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        detail = {"message": f"The name {name} is invalid"}
        super().__init__(detail, headers)
