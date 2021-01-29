from pydantic import BaseSettings


class Settings(BaseSettings):
    s3_endpoint: str = "localhost"
    s3_access_key: str = "access_key"
    s3_secret_key: str = "secret_key"
    s3_bucket: str = "multiparts"

    class Config:
        env_file = ".env"


settings = Settings()