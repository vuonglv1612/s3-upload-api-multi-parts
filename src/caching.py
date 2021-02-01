import aioredis
from src.exceptions.caching import (
    MultipartUploadFileNotMatch,
    MultipartUploadNotFound,
)


class MultipartUploadCaching(object):
    def __init__(self, redis_uri: str, upload_id: str, file_name: str):
        self._redis_uri = redis_uri
        self.upload_id = upload_id
        self.file_name = file_name
        self.redis = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await self.close()

    async def connect(self):
        self.redis = await aioredis.create_redis_pool(self._redis_uri)
        data = await self.redis.hget(self.upload_id, "file_name")
        if not data:
            raise MultipartUploadNotFound(self.upload_id)
        if self.file_name != data.decode("utf-8"):
            raise MultipartUploadFileNotMatch(
                upload_id=self.upload_id, file_name=self.file_name
            )

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def add_part(self, part):
        # {'PartNumber': part_number, 'ETag': part['ETag']}
        await self.redis.hset(self.upload_id, part["PartNumber"], part["ETag"])

    async def save(self):
        await self.redis.hset(self.upload_id, "file_name", self.file_name)

    async def get_parts(self):
        data = await self.redis.hgetall(self.upload_id)
        part_list = []
        for part in list(data.items()):
            if part[0].decode("utf-8") == "file_name":
                continue
            else:
                part_list.append(
                    {
                        "PartNumber": int(part[0].decode("utf-8")),
                        "ETag": part[1].decode("utf-8"),
                    }
                )
        return part_list

    async def delete(self):
        await self.redis.delete(self.upload_id)
