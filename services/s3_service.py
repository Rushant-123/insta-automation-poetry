import os
import logging
import requests
from config.settings import settings
from requests_toolbelt.multipart.encoder import MultipartEncoder

logger = logging.getLogger(__name__)

class EC2UploadService:
    """Service for uploading videos to EC2 endpoint."""

    def __init__(self):
        self.upload_url = settings.ec2_upload_url
        self.access_token = settings.ec2_access_token
        self.account_id = settings.ec2_account_id

    async def upload_video(
        self,
        local_file_path: str,
        caption: str,
        video_type: str = "poetry",
        reel_id: str = None
    ) -> str:
        """
        Upload a video file to the EC2 endpoint.

        Args:
            local_file_path: Path to the local video file
            caption: Caption for the video (poem text)
            video_type: Type prefix for filename
            reel_id: Unique identifier for the video
        Returns:
            URL or response from EC2
        """
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Video file not found: {local_file_path}")
        if not reel_id:
            reel_id = os.path.splitext(os.path.basename(local_file_path))[0]
        filename = f"{video_type}_{reel_id}.mp4"
        with open(local_file_path, 'rb') as f:
            m = MultipartEncoder(
                fields={
                    'video': (filename, f, 'video/mp4'),
                    'caption': caption,
                    'accessToken': self.access_token,
                    'accountId': self.account_id
                }
            )
            headers = {
                'Content-Type': m.content_type,
                'Content-Length': str(os.path.getsize(local_file_path))
            }
            try:
                logger.info(f"Uploading video to EC2: {filename}")
                response = requests.post(self.upload_url, data=m, headers=headers)
                if response.status_code == 200:
                    logger.info(f"Video uploaded successfully to EC2: {response.text}")
                    return response.text
                else:
                    logger.error(f"Failed to upload video to EC2: {response.status_code} {response.text}")
                    raise Exception(f"EC2 upload failed: {response.status_code} {response.text}")
            except Exception as e:
                logger.error(f"Unexpected error during EC2 upload: {e}")
                raise

    @staticmethod
    def generate_filename(video_id: str, file_extension: str = "mp4") -> str:
        return f"poetry-videos/{video_id}.{file_extension}" 