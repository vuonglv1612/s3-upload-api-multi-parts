from pydantic import BaseModel
from typing import Dict, Any, List, Optional

JSON = Dict[str, Any]


class BasicResponse(BaseModel):
    ok: bool = True
    message: str = ""


class Part(BaseModel):
    PartNumber: int
    ETag: str


class MultipartsInitBody(BaseModel):
    key: str


class MultipartsInitResponse(BaseModel):
    upload_id: str
    bucket: str
    key: str


class MultiPartsUploadPartResponse(BaseModel):
    bucket: str
    key: str
    upload_id: str
    part: Part


class MultiPartsCompleteBody(BaseModel):
    key: str
    upload_id: str
    parts: List[dict]


class MultiPartsAbortBody(BaseModel):
    key: Optional[str] = None
    upload_id: Optional[str] = None


class MultiPartsAbortResponse(BasicResponse):
    aborted: List[Any]