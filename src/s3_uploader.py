import logging
from typing import Any, Dict, List, Union

import aioboto3
from boto3.s3.transfer import MB
from src.schemas import Part, PartToUpload

JSON = Dict[str, Any]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("S3Uploader")


def as_percent(num, denom):
    return float(num) / float(denom) * 100.0


class S3Uploader:
    PART_MINIMUM = 5 * MB
    PART_NUMBER_MAXIMUM = 10_000

    def __init__(self, endpoint: str, access_key: str, secret_key: str):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def _create_client(self):
        return aioboto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    async def abort_all(self, bucket: str) -> List[JSON]:
        aborted = []
        async with self._create_client() as client:
            uploads = await client.list_multipart_uploads(Bucket=bucket)
            logger.debug(f"Bucket {bucket}: Aborting {len(uploads)} uploads")
            if "Uploads" in uploads:
                for u in uploads["Uploads"]:
                    upload_id = u["UploadId"]
                    key = u["Key"]
                    result = await client.abort_multipart_upload(
                        Bucket=bucket,
                        Key=key,
                        UploadId=upload_id,
                    )
                    aborted.append(result)
            logger.debug(f"Aborted: {aborted}")
        return aborted

    async def abort(self, bucket: str, key: str, upload_id: str) -> JSON:
        async with self._create_client() as client:
            result = await client.abort_multipart_upload(
                Bucket=bucket, Key=key, UploadId=upload_id
            )
            return result

    async def multiparts_init(self, bucket: str, key: str) -> Union[None, str]:
        upload_id = None
        async with self._create_client() as client:
            mpu = await client.create_multipart_upload(Bucket=bucket, Key=key)
            upload_id = mpu["UploadId"]
        return upload_id

    async def part_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part: bytes,
        part_number: int,
        strict: bool = False,
    ) -> Part:
        if strict:
            part_size = len(part)
            assert part_size >= self.PART_MINIMUM
            assert part_number < self.PART_NUMBER_MAXIMUM
        async with self._create_client() as client:
            result = await client.upload_part(
                Body=part,
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                PartNumber=part_number,
            )
            return Part(**{"PartNumber": part_number, "ETag": result["ETag"]})

    async def multiparts_complete(
        self, upload_id: str, bucket: str, key: str, parts: List[Dict]
    ):
        result = None
        async with self._create_client() as client:
            result = await client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        return result
