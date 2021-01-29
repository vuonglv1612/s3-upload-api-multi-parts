from fastapi.datastructures import UploadFile
from pydantic import BaseModel
from typing import Dict, Any, List

JSON = Dict[str, Any]


class BasicResponse(BaseModel):
    ok: bool = True
    message: str = ""


class Part(BaseModel):
    part_number: int
    etag: str


class PartToUpload(BaseModel):
    PartNumber: int
    ETag: str


class MultipartsInitBody(BaseModel):
    key: str


class MultipartsInitResponse(BaseModel):
    upload_id: str
    bucket: str
    key: str


class MultiPartsUploadPartResponse(BaseModel):
    key: str
    upload_id: str
    part: Part


class MultiPartsCompleteBody(BaseModel):
    key: str
    upload_id: str
    parts: List[dict]


class MultiPartsAbortBody(BaseModel):
    key: str
    upload_id: str
