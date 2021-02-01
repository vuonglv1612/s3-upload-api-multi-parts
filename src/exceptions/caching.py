from typing import Any, Dict, Optional

from src.exceptions.base import BadRequestException, NotFoundException

__all__ = ["MultipartUploadFileNotMatch", "MultipartUploadNotFound"]


class MultipartUploadNotFound(NotFoundException):
    def __init__(
        self, upload_id: str, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        detail = {"message": f"UploadId {upload_id} could not be found"}
        super().__init__(detail, headers)


class MultipartUploadFileNotMatch(BadRequestException):
    def __init__(
        self,
        upload_id: str,
        file_name: str,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        detail = {
            "message": f"UploadId {upload_id} does not match file {file_name}"
        }
        super().__init__(detail, headers)
