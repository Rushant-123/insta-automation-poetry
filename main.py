from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
import logging
import os
from typing import Dict

from config.settings import settings
from config.themes import get_theme_config, get_available_themes, THEME_CONFIGS
from models.schemas import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    HealthResponse,
    ThemeListResponse
)
from services.video_service import VideoService
from services.poetry_service import PoetryService
from services.s3_service import S3Service
from services.background_service import BackgroundService
from services.audio_service import AudioService
from services.tts_service import TTSService
from services.poetry_scraper import PoetryScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
video_service = None
poetry_service = None
s3_service = None
background_service = None
audio_service = None
tts_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global video_service, poetry_service, s3_service, background_service, audio_service, tts_service
    
    try:
        logger.info("Initializing services...")
        
        # Initialize core services
        poetry_service = PoetryService()
        s3_service = S3Service()
        background_service = BackgroundService()
        audio_service = AudioService()
        tts_service = TTSService()
        video_service = VideoService(s3_service, background_service, audio_service, tts_service)
        
        # Initialize content collections
        await poetry_service.initialize()
        
        # Optionally initialize background videos and audio (can be slow)
        # Uncomment these lines to auto-fetch content on startup:
        # await background_service.initialize_backgrounds()
        # await audio_service.initialize_audio_collection()
        
        logger.info("Services initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        logger.info("Shutting down services...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for generating poetry videos with peaceful backgrounds",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version="1.0.0"
    )


@app.get("/themes", response_model=ThemeListResponse)
async def get_themes():
    """Get available themes and their configurations."""
    themes = []
    for theme_type, config in THEME_CONFIGS.items():
        themes.append({
            "id": theme_type.value,
            "name": config["name"],
            "description": config["description"],
            "color_palette": config["color_palette"]
        })
    
    return ThemeListResponse(themes=themes)


@app.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_poetry_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate a poetry video with specified theme and settings."""
    try:
        # Generate unique video ID
        video_id = str(uuid.uuid4())
        
        logger.info(f"Starting video generation {video_id} with theme: {request.theme}")
        
        # Get theme configuration
        theme_config = get_theme_config(request.theme)
        
        # Get poetry content
        if request.custom_poetry:
            poetry_lines = request.custom_poetry.strip().split('\n')
            poetry_lines = [line.strip() for line in poetry_lines if line.strip()]
            logger.info(f"Using custom poetry: {poetry_lines}")
        else:
            poetry = await poetry_service.get_poetry_for_theme(
                theme_config["poetry_themes"],
                min_lines=settings.min_lines,
                max_lines=settings.max_lines
            )
            poetry_lines = poetry.lines
            logger.info(f"Using curated poetry: {poetry_lines}")
        
        # Validate poetry length
        if len(poetry_lines) < settings.min_lines:
            raise HTTPException(
                status_code=400,
                detail=f"Poetry must have at least {settings.min_lines} lines"
            )
        
        if len(poetry_lines) > settings.max_lines:
            poetry_lines = poetry_lines[:settings.max_lines]
        
        # Handle voice parameter - support both old and new formats
        enable_voiceover = request.enable_voiceover or False
        voice_style = request.voice_style or "edge_female_calm"
        
        # Check if voice is specified as a direct parameter (backward compatibility)
        if request.voice:
            enable_voiceover = True
            voice_style = request.voice
        
        # Log TTS configuration
        if enable_voiceover:
            logger.info(f"Voice-over enabled with style: {voice_style}")
        else:
            logger.info("Voice-over disabled")
        
        # Generate video
        video_url = await video_service.generate_video(
            video_id=video_id,
            poetry_lines=poetry_lines,
            theme_config=theme_config,
            theme_name=request.theme,
            custom_background=request.custom_background,
            text_style_override=request.text_style,
            animation_override=request.animation,
            duration_override=request.duration,
            enable_voiceover=enable_voiceover,
            voice_style=voice_style,
            speaking_rate=request.speaking_rate or 0.85
        )
        
        logger.info(f"Video generation completed: {video_id}")
        
        return VideoGenerationResponse(
            success=True,
            video_url=video_url,
            video_id=video_id,
            theme=request.theme,
            poetry_lines=poetry_lines,
            duration=request.duration or settings.video_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        return VideoGenerationResponse(
            success=False,
            video_id=video_id if 'video_id' in locals() else str(uuid.uuid4()),
            theme=request.theme,
            poetry_lines=[],
            duration=0,
            error_message=str(e)
        )


@app.get("/poetry/random")
async def get_random_poetry():
    """Get a random poetry for testing."""
    try:
        poetry = await poetry_service.get_random_poetry()
        return {
            "lines": poetry.lines,
            "author": poetry.author,
            "title": poetry.title,
            "source": poetry.source
        }
    except Exception as e:
        logger.error(f"Failed to get random poetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/content/fetch-backgrounds")
async def fetch_backgrounds(theme: str = "nature", count: int = 5):
    """Fetch background videos for a specific theme."""
    try:
        from config.themes import ThemeType
        
        # Validate theme
        theme_enum = None
        for t in ThemeType:
            if t.value == theme:
                theme_enum = t
                break
                
        if not theme_enum:
            raise HTTPException(status_code=400, detail=f"Invalid theme: {theme}")
            
        if not background_service:
            raise HTTPException(status_code=503, detail="Background service not available")
            
        files = await background_service.fetch_backgrounds_for_theme(theme_enum, count)
        
        return {
            "success": True,
            "theme": theme,
            "count": len(files),
            "files": [os.path.basename(f) for f in files]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch backgrounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/content/fetch-audio")
async def fetch_audio_endpoint(count: int = 10):
    """Fetch peaceful background music from Beatoven.ai for poetry videos."""
    try:
        logger.info(f"Fetching {count} peaceful audio tracks from Beatoven.ai")
        
        if not audio_service.beatoven_api_key or audio_service.beatoven_api_key == 'your_beatoven_api_key_here':
            return {
                "success": False,
                "error": "Beatoven API key not configured",
                "setup_instructions": audio_service.get_setup_instructions()
            }
        
        audio_files = await audio_service.fetch_peaceful_music(count)
        
        if audio_files:
            # Extract just filenames for response
            filenames = [os.path.basename(f) for f in audio_files]
            
            return {
                "success": True,
                "count": len(audio_files),
                "files": filenames,
                "source": "Beatoven.ai",
                "message": f"Successfully fetched {len(audio_files)} Beatoven tracks"
            }
        else:
            return {
                "success": False,
                "count": 0,
                "error": "Failed to fetch music from Beatoven.ai",
                "troubleshooting": audio_service.get_setup_instructions()
            }
            
    except Exception as e:
        logger.error(f"Failed to fetch Beatoven audio: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error fetching from Beatoven.ai"
        }


@app.post("/content/fetch-poetry")
async def fetch_poetry(source: str = "all", count: int = 20):
    """Fetch poetry from various sources."""
    try:
        from services.poetry_scraper import PoetryScraper
        
        async with PoetryScraper() as scraper:
            if source == "reddit":
                poems = await scraper.scrape_reddit_poetry(limit=count)
            elif source == "poetry_foundation":
                poems = await scraper.scrape_poetry_foundation(limit=count)
            elif source == "poets_org":
                poems = await scraper.scrape_poets_org(limit=count)
            elif source == "all":
                poems = await scraper.scrape_all_sources(poems_per_source=count//3)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
                
        # Add to poetry service
        for poem in poems:
            await poetry_service.add_custom_poetry(
                lines=poem.lines,
                author=poem.author,
                title=poem.title
            )
            
        return {
            "success": True,
            "source": source,
            "count": len(poems),
            "poems": [
                {
                    "title": p.title,
                    "author": p.author,
                    "lines_count": len(p.lines)
                } for p in poems[:10]  # Show first 10
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch poetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/content/status")
async def get_content_status():
    """Get status of all content collections."""
    try:
        # Count backgrounds
        backgrounds_count = 0
        if os.path.exists(settings.backgrounds_dir):
            backgrounds_count = len([
                f for f in os.listdir(settings.backgrounds_dir)
                if f.lower().endswith(('.mp4', '.mov', '.avi'))
            ])
            
        # Count audio
        audio_count = 0
        if os.path.exists(settings.audio_dir):
            audio_count = len([
                f for f in os.listdir(settings.audio_dir)
                if f.lower().endswith(('.mp3', '.wav', '.m4a'))
            ])
            
        # Count poetry
        poetry_count = len(poetry_service.poetry_database) if poetry_service else 0
        
        return {
            "backgrounds": {
                "count": backgrounds_count,
                "directory": settings.backgrounds_dir
            },
            "audio": {
                "count": audio_count,
                "directory": settings.audio_dir
            },
            "poetry": {
                "count": poetry_count,
                "sources": list(set(p.source for p in poetry_service.poetry_database)) if poetry_service else []
            },
            "api_keys": {
                "pexels": os.getenv('PEXELS_API_KEY', 'not_configured'),
                "pixabay": os.getenv('PIXABAY_API_KEY', 'not_configured')
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get content status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/content/test-audio-apis")
async def test_audio_apis():
    """Test if Beatoven API is working."""
    try:
        api_status = await audio_service.test_apis()
        
        return {
            "success": True,
            "api_status": api_status,
            "beatoven_configured": audio_service.beatoven_api_key != 'your_beatoven_api_key_here',
            "status_summary": audio_service.get_api_status_summary(),
            "message": "Beatoven API connection test completed"
        }
    except Exception as e:
        logger.error(f"Failed to test APIs: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to test Beatoven API"
        }

@app.post("/content/download-real-music")
async def download_real_music(count: int = 3):
    """Download music EXCLUSIVELY from Beatoven.ai API."""
    try:
        logger.info(f"Downloading {count} tracks from Beatoven.ai")
        
        if not audio_service.beatoven_api_key or audio_service.beatoven_api_key == 'your_beatoven_api_key_here':
            return {
                "success": False,
                "error": "Beatoven API key not configured",
                "setup_guide": audio_service.get_setup_instructions()
            }
        
        downloaded_files = await audio_service.fetch_peaceful_music(count)
        
        if downloaded_files:
            # Extract just filenames for response
            filenames = [os.path.basename(f) for f in downloaded_files]
            
            return {
                "success": True,
                "downloaded": len(downloaded_files),
                "files": filenames,
                "source": "Beatoven.ai API",
                "message": f"Downloaded {len(downloaded_files)} tracks from Beatoven.ai"
            }
        else:
            return {
                "success": False,
                "downloaded": 0,
                "error": "Failed to download any music from Beatoven.ai",
                "troubleshooting": audio_service.get_setup_instructions()
            }
    except Exception as e:
        logger.error(f"Failed to download Beatoven music: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error downloading from Beatoven.ai"
        }

@app.get("/content/audio-setup-guide")
async def get_audio_setup_guide():
    """Get comprehensive guide for setting up Beatoven.ai API."""
    try:
        # Count existing audio files
        audio_files = []
        if os.path.exists(audio_service.audio_dir):
            audio_files = [
                f for f in os.listdir(audio_service.audio_dir)
                if f.lower().endswith(('.mp3', '.wav', '.m4a'))
            ]
        
        # Test API status
        api_status = await audio_service.test_apis()
        
        return {
            "current_audio_files": len(audio_files),
            "files": audio_files,
            "beatoven_api_configured": audio_service.beatoven_api_key != 'your_beatoven_api_key_here',
            "setup_instructions": audio_service.get_setup_instructions(),
            "api_status": api_status,
            "recommended_approach": {
                "step_1": "🎵 Beatoven.ai is the EXCLUSIVE music source",
                "step_2": "📧 Contact hello@beatoven.ai for API access",
                "step_3": "🔑 Set BEATOVEN_API_KEY environment variable",
                "step_4": "✅ Test API with /content/test-audio-apis",
                "current_status": audio_service.get_api_status_summary(),
                "no_fallbacks": "⚠️ No fallback music generation - Beatoven only!"
            }
        }
    except Exception as e:
        logger.error(f"Failed to generate audio setup guide: {e}")
        return {
            "error": str(e),
            "message": "Failed to generate setup guide"
        }


@app.get("/content/voice-options")
async def get_voice_options():
    """Get available voice options for TTS."""
    try:
        voice_options = await tts_service.get_voice_options()
        return {
            "success": True,
            "voices": voice_options,
            "default_voice": "edge_female_calm",
            "default_speaking_rate": 0.85,
            "speaking_rate_range": {
                "min": 0.5,
                "max": 2.0,
                "default": 0.85,
                "description": "0.5=slow, 1.0=normal, 2.0=fast"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get voice options: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get voice options"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    ) 