import time

import aiofiles
from boto3.s3.transfer import KB
from fastapi import FastAPI, File, UploadFile, status

from src.s3_uploader import S3Uploader
from src.schemas import (
    BasicResponse,
    MultiPartsAbortBody,
    MultiPartsAbortResponse,
    MultiPartsCompleteBody,
    MultipartsInitBody,
    MultipartsInitResponse,
    MultiPartsUploadPartResponse,
)
from src.settings import settings
from src.utils import create_temp_filename, logger

app = FastAPI()


def create_s3_uploader() -> S3Uploader:
    return S3Uploader(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
    )


@app.post(
    "/multipart/init",
    response_model=MultipartsInitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def multipart_init(body: MultipartsInitBody):
    s3 = create_s3_uploader()
    upload_id = await s3.multiparts_init(bucket=body.bucket, key=body.key)
    return {
        "upload_id": upload_id,
        "bucket": body.bucket,
        "key": body.key,
    }


@app.post(
    "/multipart/upload_part",
    response_model=MultiPartsUploadPartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def part_upload(
    bucket: str,
    key: str,
    upload_id: str,
    part_number: int,
    file: UploadFile = File(...),
):
    file_name = create_temp_filename(file.filename)
    start = time.time()
    logger.info(f"Saving file {file_name}")
    async with aiofiles.open(file_name, "wb") as f:
        while True:
            chunk = await file.read(settings.temp_saving_chunk_size * KB)
            if not chunk:
                break
            await f.write(chunk)  # type: ignore
    logger.info(f"Saved file {file_name}")
    s3 = create_s3_uploader()
    with open(file_name, "rb") as f:
        logger.info(f"Uploading {file_name}")
        part = await s3.part_upload(
            bucket=bucket,
            key=key,
            upload_id=upload_id,
            part=f,
            part_number=part_number,
        )
        stop = time.time()
        logger.info(f"Uploaded file {file_name}. Done in {stop - start}")
        return {
            "bucket": bucket,
            "upload_id": upload_id,
            "key": key,
            "part": part,
        }


@app.post(
    "/multipart/complete",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
)
async def multiparts_complete(body: MultiPartsCompleteBody):
    s3 = create_s3_uploader()
    try:
        upload_id = await s3.multiparts_complete(
            upload_id=body.upload_id,
            bucket=body.bucket,
            key=body.key,
            parts=body.parts,
        )
    except Exception as e:
        return {"ok": False, "message": str(e)}
    else:
        return {"ok": True, "message": "completed"}


@app.post(
    "/multipart/abort",
    response_model=MultiPartsAbortResponse,
    status_code=status.HTTP_200_OK,
)
async def abort(body: MultiPartsAbortBody):
    s3 = create_s3_uploader()
    try:
        aborted = await s3.abort_all(
            bucket=body.bucket, key=body.key, upload_id=body.upload_id
        )
    except Exception as e:
        print(e)
        return {"ok": False, "message": str(e), "aborted": []}
    else:
        return {"ok": True, "message": "aborted", "aborted": aborted}
