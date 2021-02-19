import time

import aiofiles
import aiofiles.os
from fastapi import FastAPI, status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.caching import MultipartUploadCaching
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
from src.utils import create_temp_filename, logger, nomalize_file_name

app = FastAPI()


def create_s3_uploader() -> S3Uploader:
    return S3Uploader(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
    )


@app.get("/", include_in_schema=False)
@app.get("/home", include_in_schema=False)
async def redirect_home_to_docs():
    return RedirectResponse(url="/docs")


@app.post(
    "/multipart/init",
    response_model=MultipartsInitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def multipart_init(body: MultipartsInitBody):
    s3 = create_s3_uploader()
    upload_id = await s3.multiparts_init(
        bucket=settings.s3_bucket, key=body.key
    )
    return {
        "upload_id": upload_id,
        "bucket": settings.s3_bucket,
        "key": body.key,
    }


@app.post(
    "/multipart/upload_part",
    response_model=MultiPartsUploadPartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def part_upload(
    name: str, upload_id: str, part_number: int, request: Request
):
    name = nomalize_file_name(name)
    temp_file_name = create_temp_filename(name)
    start = time.time()
    logger.info(
        f"[{upload_id}]Saving key: {name} part: {part_number} to file {temp_file_name}"
    )
    async with aiofiles.open(temp_file_name, "wb") as f:
        async for chunk in request.stream():
            await f.write(chunk)  # type: ignore
    logger.info(
        f"[{upload_id}]Saved key: {name} part {part_number} to file {temp_file_name}"
    )
    s3 = create_s3_uploader()
    try:
        with open(temp_file_name, "rb") as f:
            logger.info(
                f"[{upload_id}]Uploading key: {name} part: {part_number} to bucket {settings.s3_bucket}"
            )
            part = await s3.part_upload(
                bucket=settings.s3_bucket,
                key=name,
                upload_id=upload_id,
                part=f,
                part_number=part_number,
            )
        stop = time.time()
        logger.info(
            f"{upload_id}Uploaded key: {name} part: {part_number}. Done in {stop - start}"
        )
    except Exception as exec:
        logger.exception("ERROR: %s", exec)
        raise exec
    finally:
        logger.info(f"{upload_id}Deleting key: {name} part: {part_number}")
        await aiofiles.os.remove(temp_file_name)
        logger.info(f"{upload_id}Deleted key: {name} part: {part_number}")
    return {
        "bucket": settings.s3_bucket,
        "upload_id": upload_id,
        "key": name,
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
            bucket=settings.s3_bucket,
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
            bucket=settings.s3_bucket, key=body.key, upload_id=body.upload_id
        )
    except Exception as e:
        print(e)
        return {"ok": False, "message": str(e), "aborted": []}
    else:
        return {"ok": True, "message": "aborted", "aborted": aborted}
