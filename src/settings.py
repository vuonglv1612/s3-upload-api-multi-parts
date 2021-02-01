from pydantic import BaseSettings


class Settings(BaseSettings):
    s3_endpoint: str = "localhost"
    s3_access_key: str = "access_key"
    s3_secret_key: str = "secret_key"
    temp_saving_chunk_size: int = 1024  # KB
    caching_parts_redis_uri: str = "redis://"

    class Config:
        env_file = ".env"


settings = Settings()