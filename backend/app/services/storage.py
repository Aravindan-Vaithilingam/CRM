from pathlib import Path
import boto3
from app.core.config import settings

_LOCAL_DIR = Path('uploads')

class StorageService:
    def __init__(self):
        self.mode = settings.STORAGE_MODE.lower()
        self.s3 = boto3.client('s3', region_name=settings.AWS_REGION) if self.mode == 's3' else None

    def save(self, key: str, data: bytes) -> str:
        if self.mode == 's3':
            self.s3.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=data)
            return key
        _LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        path = _LOCAL_DIR / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

storage = StorageService()
