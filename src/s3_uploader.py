from io import BufferedReader
from typing import Any, Dict, List, Union

import aioboto3
from boto3.s3.transfer import MB

from src.schemas import Part, JSON
from src.utils import logger


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

    async def abort_all(
        self, bucket: str, key: str = None, upload_id: str = None
    ) -> List[JSON]:
        aborted = []
        async with self._create_client() as client:
            uploads = await client.list_multipart_uploads(Bucket=bucket)
            logger.debug(f"Bucket {bucket}: Aborting {len(uploads)} uploads")
            if "Uploads" not in uploads:
                return aborted
            for u in uploads["Uploads"]:
                uid = u["UploadId"]
                if upload_id and upload_id != uid:
                    continue
                k = u["Key"]
                if key and key != k:
                    continue
                result = await client.abort_multipart_upload(
                    Bucket=bucket,
                    Key=k,
                    UploadId=uid,
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
        part: BufferedReader,
        part_number: int,
    ) -> Part:
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
