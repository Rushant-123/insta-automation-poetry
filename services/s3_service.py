import boto3
from botocore.exceptions import ClientError
import os
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for uploading videos to S3 and generating URLs."""
    
    def __init__(self):
        """Initialize S3 client."""
        if settings.aws_access_key_id and settings.aws_secret_access_key and settings.s3_bucket_name:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.s3_bucket_name
            self.enabled = True
        else:
            logger.warning("S3 credentials not configured. S3 functionality will be disabled.")
            self.s3_client = None
            self.bucket_name = None
            self.enabled = False
        
    async def upload_video(
        self,
        local_file_path: str,
        s3_key: str,
        content_type: str = "video/mp4"
    ) -> str:
        """
        Upload a video file to S3.
        
        Args:
            local_file_path: Path to the local video file
            s3_key: S3 object key (path in bucket)
            content_type: MIME type of the file
            
        Returns:
            S3 URL of the uploaded video (or local file path if S3 disabled)
        """
        if not self.enabled:
            # Return local file path when S3 is disabled (for testing)
            logger.info(f"S3 disabled - video saved locally: {local_file_path}")
            return f"file://{local_file_path}"
            
        try:
            logger.info(f"Uploading video to S3: {s3_key}")
            
            # Upload file to S3
            self.s3_client.upload_file(
                local_file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type
                    # Note: ACL removed - bucket should be configured with public read policy
                }
            )
            
            # Generate URL
            if settings.s3_base_url:
                video_url = f"{settings.s3_base_url}/{s3_key}"
            else:
                video_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            return video_url
            
        except ClientError as e:
            logger.error(f"Failed to upload video to S3: {e}")
            raise Exception(f"S3 upload failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            raise
            
    async def delete_video(self, s3_key: str) -> bool:
        """
        Delete a video from S3.
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Video deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete video from S3: {e}")
            return False
            
    def generate_s3_key(self, video_id: str, file_extension: str = "mp4") -> str:
        """
        Generate S3 key for a video.
        
        Args:
            video_id: Unique video identifier
            file_extension: File extension
            
        Returns:
            S3 key string
        """
        return f"poetry-videos/{video_id}.{file_extension}"
        
    async def check_bucket_exists(self) -> bool:
        """
        Check if the configured S3 bucket exists and is accessible.
        
        Returns:
            True if bucket exists and is accessible
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False 