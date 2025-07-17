from pydantic import BaseModel, Field
from typing import Optional, List
from config.themes import ThemeType, TextStyle, AnimationType


class VideoGenerationRequest(BaseModel):
    """Request model for generating a poetry video."""
    theme: ThemeType = Field(
        default=ThemeType.NATURE,
        description="Theme for the video background and styling"
    )
    text_style: Optional[TextStyle] = Field(
        default=None,
        description="Text style override (uses theme default if not specified)"
    )
    animation: Optional[AnimationType] = Field(
        default=None,
        description="Animation type override (uses theme default if not specified)"
    )
    custom_poetry: Optional[str] = Field(
        default=None,
        description="Custom poetry text (uses curated poetry if not provided)"
    )
    custom_background: Optional[str] = Field(
        default=None,
        description="Custom background video URL (uses theme backgrounds if not provided)"
    )
    duration: Optional[int] = Field(
        default=None,
        ge=10,
        le=30,
        description="Video duration in seconds (10-30, uses default if not specified)"
    )
    enable_voiceover: Optional[bool] = Field(
        default=False,
        description="Enable voice-over narration for the poetry"
    )
    voice_style: Optional[str] = Field(
        default="edge_female_calm",
        description="Voice style for TTS (edge_female_calm, edge_female_warm, edge_male_calm, etc.)"
    )
    voice: Optional[str] = Field(
        default=None,
        description="Voice style (backward compatibility - same as voice_style, auto-enables voiceover)"
    )
    speaking_rate: Optional[float] = Field(
        default=0.85,
        ge=0.5,
        le=2.0,
        description="Speaking rate for voice-over (0.5-2.0, 1.0 = normal)"
    )


class VideoGenerationResponse(BaseModel):
    """Response model for poetry video generation."""
    success: bool
    video_url: Optional[str] = Field(
        default=None,
        description="S3 URL of the generated video"
    )
    video_id: str = Field(
        description="Unique identifier for the generated video"
    )
    theme: ThemeType
    poetry_lines: List[str] = Field(
        description="The poetry lines used in the video"
    )
    duration: int = Field(
        description="Actual duration of the generated video in seconds"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if generation failed"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


class ThemeListResponse(BaseModel):
    """Response model for available themes."""
    themes: List[dict] = Field(
        description="List of available themes with their configurations"
    )


class PoetryResponse(BaseModel):
    """Response model for poetry content."""
    lines: List[str]
    author: Optional[str] = None
    title: Optional[str] = None
    source: str 