from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Settings
    app_name: str = "Poetry Video Generator"
    debug: bool = False
    
    # AWS S3 Settings
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None
    s3_base_url: Optional[str] = None
    
    # Azure OpenAI Settings
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: str = "2025-03-01-preview"
    azure_openai_model: str = "onyx"
    azure_openai_deployment_name: Optional[str] = None
    azure_openai_tts_endpoint: Optional[str] = None
    azure_openai_tts_api_key: Optional[str] = None
    azure_openai_tts_api_version: Optional[str] = None
    pexels_api_key: Optional[str] = None
    
    # Video Settings
    video_width: int = 1080
    video_height: int = 1920
    video_duration: int = 18  # seconds
    video_fps: int = 24
    
    # Audio Settings
    audio_fade_duration: float = 1.0  # seconds
    
    # File Paths
    temp_dir: str = "./temp"
    assets_dir: str = "./assets"
    backgrounds_dir: str = "./assets/backgrounds"
    audio_dir: str = "./audio/drive-download-20250721T081448Z-1-001"
    
    # Poetry Settings
    min_lines: int = 4
    max_lines: int = 8
    
    # EC2 Upload Settings
    ec2_upload_url: str = "http://44.208.29.67:3000/api/upload-reel"
    ec2_access_token: str = "IGAAT3YhbJjzdBZAFBrYkZA0RjNQVjliM0VtZAmRRU00yVWlqOWdUaHJZAd3hlUEZAJSWlvWmp3T3ZAJSEdxRjBOYTU2aE1nLXE5b3ljdUJDMnRNTTUwYWZAZASW9xYmI0ZAHVMZA0hoRmlNYURUWjBKUVItSDkwRmg2dUZAzTXhHOHRCQkpyOAZDZD"
    ec2_account_id: str = "17841473376710062"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.temp_dir, exist_ok=True)
os.makedirs(settings.assets_dir, exist_ok=True)
os.makedirs(settings.backgrounds_dir, exist_ok=True)
os.makedirs(settings.audio_dir, exist_ok=True) 