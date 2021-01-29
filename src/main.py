import logging
from typing import List

from fastapi import FastAPI, File, UploadFile, Body
from fastapi import status
from fastapi.param_functions import Query
from pydantic import Field
from starlette.status import HTTP_200_OK

from src.s3_uploader import S3Uploader
from src.settings import settings
from src.schemas import (
    JSON,
    BasicResponse,
    MultipartsInitResponse,
    MultipartsInitBody,
    MultiPartsUploadPartResponse,
    MultiPartsCompleteBody,
    MultiPartsAbortBody,
)

logging.basicConfig(level=logging.DEBUG)


app = FastAPI()


def create_s3_uploader() -> S3Uploader:
    return S3Uploader(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
    )


@app.post(
    "/init_multipart",
    response_model=MultipartsInitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def multipart_init(body: MultipartsInitBody):
    s3 = create_s3_uploader()
    print(body)
    upload_id = await s3.multiparts_init(
        bucket=settings.s3_bucket, key=body.key
    )
    return {
        "upload_id": upload_id,
        "bucket": settings.s3_bucket,
        "key": body.key,
    }


@app.post(
    "/upload_part",
    response_model=MultiPartsUploadPartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def part_upload(
    upload_id: str,
    key: str,
    part_number: int,
    file: UploadFile = File(...),
):
    s3 = create_s3_uploader()
    data = await file.read()
    part = await s3.part_upload(
        bucket=settings.s3_bucket,
        key=key,
        upload_id=upload_id,
        part=data,
        part_number=part_number,
    )
    return {"upload_id": upload_id, "key": key, "part": part}


@app.post(
    "/complete_multipart",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
)
async def multiparts_complete(body: MultiPartsCompleteBody):
    s3 = create_s3_uploader()
    try:
        upload_id = await s3.multiparts_complete(
            upload_id=body.upload_id,
            bucket=settings.s3_bucket,
            key=body.key,
            parts=body.parts,
        )
    except Exception as e:
        return {"ok": False, "message": str(e)}
    else:
        return {"ok": True, "message": "completed"}


@app.post(
    "/abort", response_model=BasicResponse, status_code=status.HTTP_200_OK
)
async def abort(body: MultiPartsAbortBody):
    s3 = create_s3_uploader()
    try:
        await s3.abort(
            bucket=settings.s3_bucket, key=body.key, upload_id=body.upload_id
        )
    except Exception as e:
        print(e)
        return {"ok": False, "message": str(e)}
    else:
        return {"ok": True, "message": "aborted"}


@app.post(
    "/abort_all", response_model=BasicResponse, status_code=status.HTTP_200_OK
)
async def abort_all_part():
    s3 = create_s3_uploader()
    try:
        await s3.abort_all(settings.s3_bucket)
    except Exception as e:
        print(e)
        return {"ok": False, "message": str(e)}
    else:
        return {"ok": True, "message": "aborted"}
