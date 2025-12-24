"""
MathVerse Animation Engine - Storage Utilities
Handles uploading rendered videos to cloud storage and generating presigned URLs.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StorageBackend:
    """Abstract base class for storage backends"""
    
    def upload(self, local_path: str, remote_path: str) -> str:
        """Upload file and return URL"""
        raise NotImplementedError
    
    def upload_bytes(self, data: bytes, remote_path: str) -> str:
        """Upload bytes and return URL"""
        raise NotImplementedError
    
    def get_presigned_url(self, remote_path: str, expiry_seconds: int = 3600) -> str:
        """Get presigned URL for downloading"""
        raise NotImplementedError
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from storage"""
        raise NotImplementedError
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists"""
        raise NotImplementedError
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get file size in bytes"""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend"""
    
    def __init__(self, base_path: str = "/tmp/mathverse_output"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path}")
    
    def upload(self, local_path: str, remote_path: str) -> str:
        """Copy file to local storage directory"""
        local = Path(local_path)
        remote = self.base_path / remote_path
        
        # Create directories if needed
        remote.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(local, remote)
        
        url = f"file://{remote}"
        logger.info(f"Uploaded {local_path} -> {remote}")
        return url
    
    def upload_bytes(self, data: bytes, remote_path: str) -> str:
        """Write bytes to local file"""
        remote = self.base_path / remote_path
        remote.parent.mkdir(parents=True, exist_ok=True)
        
        with open(remote, 'wb') as f:
            f.write(data)
        
        url = f"file://{remote}"
        logger.info(f"Uploaded bytes -> {remote}")
        return url
    
    def get_presigned_url(self, remote_path: str, expiry_seconds: int = 3600) -> str:
        """For local storage, return file:// URL"""
        remote = self.base_path / remote_path
        return f"file://{remote}"
    
    def delete(self, remote_path: str) -> bool:
        """Delete local file"""
        remote = self.base_path / remote_path
        if remote.exists():
            remote.unlink()
            logger.info(f"Deleted {remote}")
            return True
        return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if local file exists"""
        return (self.base_path / remote_path).exists()
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get local file size"""
        remote = self.base_path / remote_path
        if remote.exists():
            return remote.stat().st_size
        return None


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend with presigned URLs"""
    
    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        expiry_seconds: int = 3600
    ):
        self.bucket = bucket
        self.region = region
        self.expiry_seconds = expiry_seconds
        
        # Initialize boto3 client
        try:
            import boto3
            self.boto3 = boto3
            
            config = {}
            if access_key and secret_key:
                config['aws_access_key_id'] = access_key
                config['aws_secret_access_key'] = secret_key
            if endpoint:
                # For S3-compatible services like MinIO
                config['endpoint_url'] = endpoint
            
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                **config
            )
            logger.info(f"S3 storage initialized for bucket: {bucket}")
        except ImportError:
            logger.warning("boto3 not installed, S3 storage unavailable")
            self.s3_client = None
    
    def upload(self, local_path: str, remote_path: str) -> str:
        """Upload file to S3"""
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
        
        self.s3_client.upload_file(local_path, self.bucket, remote_path)
        
        url = self._get_object_url(remote_path)
        logger.info(f"Uploaded {local_path} -> s3://{self.bucket}/{remote_path}")
        return url
    
    def upload_bytes(self, data: bytes, remote_path: str) -> str:
        """Upload bytes to S3"""
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
        
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=remote_path,
            Body=data,
            ContentType='application/octet-stream'
        )
        
        url = self._get_object_url(remote_path)
        logger.info(f"Uploaded bytes -> s3://{self.bucket}/{remote_path}")
        return url
    
    def get_presigned_url(self, remote_path: str, expiry_seconds: int = None) -> str:
        """Generate presigned URL for download"""
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
        
        if expiry_seconds is None:
            expiry_seconds = self.expiry_seconds
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': remote_path,
                    'ResponseContentDisposition': f'attachment; filename="{Path(remote_path).name}"'
                },
                ExpiresIn=expiry_seconds
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            # Fallback to regular URL
            return self._get_object_url(remote_path)
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from S3"""
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=remote_path)
            logger.info(f"Deleted s3://{self.bucket}/{remote_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in S3"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=remote_path)
            return True
        except:
            return False
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get file size from S3 metadata"""
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=remote_path)
            return response['ContentLength']
        except:
            return None
    
    def _get_object_url(self, remote_path: str) -> str:
        """Get regular (non-presigned) URL"""
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{remote_path}"


class GCStorageBackend(StorageBackend):
    """Google Cloud Storage backend"""
    
    def __init__(
        self,
        bucket: str,
        project_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        expiry_seconds: int = 3600
    ):
        self.bucket = bucket
        self.expiry_seconds = expiry_seconds
        self.client = None
        
        try:
            from google.cloud import storage as gcs
            from google.oauth2 import service_account
            
            credentials = None
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            
            self.client = gcs.Client(project=project_id, credentials=credentials)
            self.bucket_obj = self.client.bucket(bucket)
            logger.info(f"GCS storage initialized for bucket: {bucket}")
        except ImportError:
            logger.warning("google-cloud-storage not installed, GCS storage unavailable")
    
    def upload(self, local_path: str, remote_path: str) -> str:
        """Upload file to GCS"""
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        
        blob = self.bucket_obj.blob(remote_path)
        blob.upload_from_filename(local_path)
        
        url = f"gs://{self.bucket}/{remote_path}"
        logger.info(f"Uploaded {local_path} -> {url}")
        return url
    
    def upload_bytes(self, data: bytes, remote_path: str) -> str:
        """Upload bytes to GCS"""
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        
        blob = self.bucket_obj.blob(remote_path)
        blob.upload_from_string(data)
        
        url = f"gs://{self.bucket}/{remote_path}"
        logger.info(f"Uploaded bytes -> {url}")
        return url
    
    def get_presigned_url(self, remote_path: str, expiry_seconds: int = None) -> str:
        """Generate signed URL for download"""
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        
        if expiry_seconds is None:
            expiry_seconds = self.expiry_seconds
        
        blob = self.bucket_obj.blob(remote_path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(seconds=expiry_seconds),
            method="GET"
        )
        return url
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from GCS"""
        if not self.client:
            raise RuntimeError("GCS client not initialized")
        
        blob = self.bucket_obj.blob(remote_path)
        blob.delete()
        logger.info(f"Deleted gs://{self.bucket}/{remote_path}")
        return True
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in GCS"""
        if not self.client:
            return False
        
        blob = self.bucket_obj.blob(remote_path)
        return blob.exists()
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get file size from GCS"""
        if not self.client:
            return None
        
        blob = self.bucket_obj.blob(remote_path)
        try:
            blob.reload()
            return blob.size
        except:
            return None


def get_storage_backend() -> StorageBackend:
    """Factory function to get appropriate storage backend"""
    from config.app_config import get_storage_config
    
    config = get_storage_config()
    provider = config.provider.lower()
    
    if provider == "local":
        return LocalStorageBackend(config.base_path)
    elif provider == "s3":
        return S3StorageBackend(
            bucket=config.s3_bucket or "",
            region=config.s3_region or "us-east-1",
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            endpoint=config.s3_endpoint,
            expiry_seconds=config.presigned_url_expiry
        )
    elif provider == "gcs":
        return GCStorageBackend(
            bucket=config.gcs_bucket or "",
            project_id=config.gcs_project_id,
            credentials_path=config.gcs_credentials_path,
            expiry_seconds=config.presigned_url_expiry
        )
    else:
        logger.warning(f"Unknown storage provider: {provider}, using local")
        return LocalStorageBackend(config.base_path)


class OutputManager:
    """Manages output file organization and cleanup"""
    
    def __init__(self, storage: StorageBackend = None):
        self.storage = storage or get_storage_backend()
        self.uploaded_files = []
    
    def generate_output_path(
        self,
        scene_type: str,
        level: str,
        job_id: str,
        extension: str = "mp4"
    ) -> str:
        """Generate organized output path"""
        date = datetime.utcnow().strftime("%Y/%m/%d")
        filename = f"{job_id}_{scene_type}_{level}.{extension}"
        return f"videos/{date}/{filename}"
    
    def generate_thumbnail_path(self, video_path: str) -> str:
        """Generate thumbnail path from video path"""
        path = Path(video_path)
        return str(path.with_suffix(".jpg"))
    
    def save_output(
        self,
        local_video_path: str,
        local_thumbnail_path: Optional[str],
        scene_type: str,
        level: str,
        job_id: str
    ) -> Tuple[str, Optional[str]]:
        """Save output files to storage"""
        video_path = self.generate_output_path(scene_type, level, job_id)
        thumbnail_path = None
        
        # Upload video
        video_url = self.storage.upload(local_video_path, video_path)
        self.uploaded_files.append(video_path)
        
        # Upload thumbnail if exists
        if local_thumbnail_path and Path(local_thumbnail_path).exists():
            thumb_remote = self.generate_thumbnail_path(video_path)
            thumbnail_url = self.storage.upload(local_thumbnail_path, thumb_remote)
            self.uploaded_files.append(thumb_remote)
            thumbnail_path = thumbnail_url
        
        return video_url, thumbnail_path
    
    def get_download_url(self, remote_path: str, expiry_seconds: int = 3600) -> str:
        """Get presigned download URL"""
        return self.storage.get_presigned_url(remote_path, expiry_seconds)
    
    def cleanup_local(self, paths: list):
        """Clean up local temporary files"""
        import shutil
        for path in paths:
            p = Path(path)
            if p.exists():
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)
    
    def cleanup_remote(self, remote_paths: list):
        """Clean up remote files"""
        for path in remote_paths:
            self.storage.delete(path)
        self.uploaded_files = []
