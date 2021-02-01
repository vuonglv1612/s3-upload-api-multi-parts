## UPLOADING MULTIPART S3 API  
Multi parts uploading api using S3 as storage provider.

## Project is using:
- `FastAPI`  
- `uvicorn`  
- `Docker Compose`  
- `aioboto3`  
- `redis`  

## Requirements
- `docker`  
- `docker-compose`  

## Installation
1. Clone project  
```git clone https://github.com/vuonglv1612/s3-upload-api-multi-parts.git```  
2. Create `.env` file 
```cp .env.template .env```  
3. Build project  
```docker-compose build```  
4. Run project  
```docker-compose up -d```  

## Uninstallation
```docker-compose down```

## Configuration
Edit `.env` file  
`S3_ENDPOINT`: S3 provider endpoint. Ex: `https://ss-hn-1.bizflycloud.vn`  
`S3_ACCESS_KEY`: S3 access token  
`S3_SECRET_KEY`: S3 secret token  
`TEMP_SAVING_CHUNK_SIZE`: size of temp file buffer  
`CACHING_PARTS_REDIS_URI`: redis uri is for caching uploaded parts

## Docs
```http://upload-api-domain/docs```
