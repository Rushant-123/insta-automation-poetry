import os
import tempfile
import logging
from typing import List, Optional, Dict, Any, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip,
    ColorClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
)
from moviepy.video.fx import resize, fadein as video_fadein, fadeout as video_fadeout
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.config import change_settings

# Configure ImageMagick path for MoviePy
change_settings({"IMAGEMAGICK_BINARY": "convert"})  # Use system PATH on Linux
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
import random

from config.settings import settings
from config.themes import TextStyle, AnimationType, get_theme_config
from services.s3_service import EC2UploadService
from services.tts_service import TTSService
from utils.text_animator import TextAnimator
from utils.video_composer import VideoComposer

logger = logging.getLogger(__name__)


class VideoService:
    """Service for generating poetry videos."""
    
    def __init__(self, s3_service: EC2UploadService, background_service=None, audio_service=None, tts_service=None):
        """Initialize video service."""
        self.s3_service = s3_service
        self.background_service = background_service
        self.audio_service = audio_service
        self.tts_service = tts_service or TTSService()
        self.text_animator = TextAnimator()
        self.video_composer = VideoComposer()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    async def generate_video(
        self,
        video_id: str,
        poetry_lines: List[str],
        theme_config: Dict[str, Any],
        theme_name: Optional[str] = None,
        custom_background: Optional[str] = None,
        text_style_override: Optional[TextStyle] = None,
        animation_override: Optional[AnimationType] = None,
        duration_override: Optional[int] = None,
        enable_voiceover: bool = False,
        voice_style: str = "edge_female_calm",
        speaking_rate: float = 0.85
    ) -> str:
        """
        Generate a poetry video.
        
        Args:
            video_id: Unique video identifier
            poetry_lines: List of poetry lines to display
            theme_config: Theme configuration
            custom_background: Optional custom background video URL
            text_style_override: Optional text style override
            animation_override: Optional animation override
            duration_override: Optional duration override
            enable_voiceover: Whether to generate voice-over
            voice_style: Voice style for TTS (e.g., "edge_female_calm")
            speaking_rate: Speaking rate for voice-over (0.5-2.0)
            
        Returns:
            S3 URL of the generated video
        """
        logger.info(f"Generating video {video_id}")
        
        try:
            # Get video parameters
            duration = duration_override or settings.video_duration
            width = settings.video_width
            height = settings.video_height
            fps = settings.video_fps
            
            # Get background video
            background_path = await self._get_background_video(
                theme_config, theme_name, custom_background
            )
            
            # Get audio
            audio_path = await self._get_background_audio(theme_config)
            
            # Generate voice-over if enabled
            voiceover_path = None
            if enable_voiceover:
                try:
                    voiceover_path = await self.tts_service.generate_poetry_voiceover(
                        poetry_lines, voice_style, speaking_rate
                    )
                    if voiceover_path:
                        logger.info(f"Generated voice-over: {voiceover_path}")
                    else:
                        logger.warning("Voice-over generation failed, continuing without voice-over")
                except Exception as e:
                    logger.warning(f"Voice-over generation failed: {e}")
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(
                suffix='.mp4', delete=False
            ) as tmp_file:
                output_path = tmp_file.name
                
            # Generate video in thread pool
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._create_video_sync,
                output_path,
                background_path,
                audio_path,
                voiceover_path,
                poetry_lines,
                theme_config,
                text_style_override,
                animation_override,
                duration,
                width,
                height,
                fps
            )
            
            # Upload to EC2
            poem_caption = "\n".join(poetry_lines)
            video_url = await self.s3_service.upload_video(output_path, poem_caption, video_type="poetry", reel_id=video_id)
            
            # Clean up temporary files (keep video if S3 is disabled for testing)
            try:
                if not video_url.startswith("file://"):
                    os.unlink(output_path)
                if background_path and os.path.exists(background_path):
                    os.unlink(background_path)
                if audio_path and os.path.exists(audio_path):
                    os.unlink(audio_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary files: {e}")
                
            logger.info(f"Video generation completed: {video_id}")
            return video_url
            
        except Exception as e:
            logger.error(f"Video generation failed for {video_id}: {e}")
            raise
            
    def _create_video_sync(
        self,
        output_path: str,
        background_path: Optional[str],
        audio_path: Optional[str],
        voiceover_path: Optional[str],
        poetry_lines: List[str],
        theme_config: Dict[str, Any],
        text_style_override: Optional[TextStyle],
        animation_override: Optional[AnimationType],
        duration: int,
        width: int,
        height: int,
        fps: int
    ):
        """Create video synchronously (runs in thread pool)."""
        try:
            # Determine actual video duration based on voiceover
            actual_duration = duration
            if voiceover_path and os.path.exists(voiceover_path):
                try:
                    voice_audio = AudioFileClip(voiceover_path)
                    # Use voiceover duration + 2 seconds buffer as the actual video duration
                    actual_duration = voice_audio.duration + 2.0
                    logger.info(f"Using voiceover-based duration: {actual_duration:.1f}s (voiceover: {voice_audio.duration:.1f}s + 2s buffer)")
                    voice_audio.close()
                except Exception as e:
                    logger.warning(f"Failed to get voiceover duration: {e}")
            
            # Create background clip
            if background_path and os.path.exists(background_path):
                try:
                    background = VideoFileClip(background_path)
                    # Adjust background video to match actual duration
                    if background.duration < actual_duration:
                        # Loop background if shorter than needed duration
                        loops_needed = int(actual_duration / background.duration) + 1
                        background = background.loop(duration=actual_duration)
                        logger.info(f"Looped background video to {actual_duration:.1f}s")
                    else:
                        # Cut background if longer than needed duration
                        background = background.subclip(0, actual_duration)
                        logger.info(f"Cut background video to {actual_duration:.1f}s")
                except Exception as e:
                    logger.warning(f"Failed to load background video: {e}. Using solid color.")
                    bg_color = self._hex_to_rgb(
                        theme_config["color_palette"]["accent"]
                    )
                    background = ColorClip(
                        size=(width, height),
                        color=bg_color,
                        duration=actual_duration
                    )
            else:
                # Create solid color background
                bg_color = self._hex_to_rgb(
                    theme_config["color_palette"]["accent"]
                )
                background = ColorClip(
                    size=(width, height),
                    color=bg_color,
                    duration=actual_duration
                )
                
            # Resize background to match target dimensions
            background = background.resize((width, height))
            
            # Add overlay for better text readability
            overlay_color = self._parse_rgba(
                theme_config["color_palette"]["background_overlay"]
            )
            overlay = ColorClip(
                size=(width, height),
                color=overlay_color[:3],
                duration=actual_duration
            ).set_opacity(overlay_color[3] if len(overlay_color) > 3 else 0.3)
            
            # Create text clips
            text_clips = self._create_text_clips(
                poetry_lines,
                theme_config,
                text_style_override,
                animation_override,
                actual_duration,
                width,
                height
            )
            
            # Compose final video
            video_clips = [background, overlay] + text_clips
            final_video = CompositeVideoClip(video_clips, size=(width, height))
            final_video = final_video.set_duration(actual_duration)
            
            # Handle audio: mix background music with voice-over
            final_audio = None
            bg_audio = None
            
            # Process background music FIRST
            if audio_path and os.path.exists(audio_path):
                try:
                    bg_audio = AudioFileClip(audio_path)
                    if bg_audio.duration < actual_duration:
                        # Loop the audio to fit the video duration
                        loops_needed = int(actual_duration / bg_audio.duration) + 1
                        bg_audio = concatenate_audioclips([bg_audio] * loops_needed).subclip(0, actual_duration)
                    else:
                        bg_audio = bg_audio.subclip(0, actual_duration)
                        
                    # Set background music volume based on whether voice-over is present
                    bg_volume = 0.15 if voiceover_path else 0.25  # Lowered from 0.25 to 0.15 for voice-over
                    bg_audio = bg_audio.fx(volumex, bg_volume)
                    
                    final_audio = bg_audio
                    logger.info(f"Added background music at {bg_volume*100}% volume")
                except Exception as e:
                    logger.warning(f"Failed to add background audio: {e}")
            
            # Process voice-over - DON'T loop it, just use it once
            if voiceover_path and os.path.exists(voiceover_path):
                try:
                    voice_audio = AudioFileClip(voiceover_path)
                    
                    # Don't loop voiceover - use it as is
                    # If it's longer than our duration, cut it. If shorter, that's fine.
                    if voice_audio.duration > actual_duration:
                        voice_audio = voice_audio.subclip(0, actual_duration)
                    
                    # Adjust voice-over volume
                    voice_audio = voice_audio.fx(volumex, 0.5)
                    
                    # Mix with background music if both exist
                    if final_audio:
                        try:
                            # Create a composite audio with voice-over and background music
                            final_audio = CompositeAudioClip([final_audio, voice_audio])
                            logger.info("Mixed voice-over with background music (no looping)")
                        except Exception as mix_error:
                            logger.warning(f"Failed to mix audio, using voice-over only: {mix_error}")
                            final_audio = voice_audio
                    else:
                        final_audio = voice_audio
                        logger.info("Added voice-over audio (no looping)")
                except Exception as e:
                    logger.warning(f"Failed to add voice-over: {e}")
            
            # Ensure we have some audio output
            if final_audio is None:
                logger.warning("No audio available - generating silent video")
                
            # Set final audio to video with error handling
            if final_audio:
                try:
                    final_video = final_video.set_audio(final_audio)
                    logger.info("Successfully added audio to video")
                except Exception as e:
                    logger.error(f"Failed to set audio to video: {e}")
                    logger.info("Continuing without audio")
            else:
                logger.info("No audio found - generating silent video")
                    
            # Write video file
            write_kwargs = {
                'fps': fps,
                'codec': 'libx264',
                'remove_temp': True,
                'verbose': False,
                'logger': None
            }
            
            # Only add audio codec if we have audio
            if final_audio:
                write_kwargs['audio_codec'] = 'aac'
                write_kwargs['temp_audiofile'] = 'temp-audio.m4a'
                logger.info("Writing video with audio")
            else:
                logger.info("Writing video without audio")
            
            final_video.write_videofile(output_path, **write_kwargs)
            
            # Close clips to free memory
            background.close()
            overlay.close()
            for clip in text_clips:
                clip.close()
            final_video.close()
            
        except Exception as e:
            logger.error(f"Sync video creation failed: {e}")
            raise
            
    def _create_text_clips(
        self,
        poetry_lines: List[str],
        theme_config: Dict[str, Any],
        text_style_override: Optional[TextStyle],
        animation_override: Optional[AnimationType],
        duration: int,
        width: int,
        height: int
    ) -> List:
        """Create text clips for poetry lines."""
        text_clips = []
        
        # Get text styling
        text_style = text_style_override or theme_config["text_style"]
        animation_type = animation_override or theme_config["animation"]
        
        font_family = theme_config["font_family"]
        font_size = theme_config["font_size"]
        line_spacing = theme_config["line_spacing"]
        
        primary_color = theme_config["color_palette"]["primary"]
        secondary_color = theme_config["color_palette"]["secondary"]
        
        # Calculate text positioning
        line_height = int(font_size * line_spacing)
        total_text_height = len(poetry_lines) * line_height
        start_y = (height - total_text_height) // 2
        
        # Create a semi-transparent background for all text
        text_bg_height = total_text_height + 60  # Add padding
        text_bg_width = width - 40  # Leave some margin
        text_background = ColorClip(
            size=(text_bg_width, text_bg_height),
            color=(0, 0, 0),  # Black background
            duration=duration
        ).set_opacity(0.6).set_position(('center', start_y - 30))  # 30px padding top
        
        text_clips.append(text_background)
        
        # Create individual line clips
        for i, line in enumerate(poetry_lines):
            if not line.strip():
                continue
                
            y_position = start_y + (i * line_height)
            
            # Create text clip
            font_path = self._get_font_path(font_family, text_style)
            txt_clip = TextClip(
                line.strip(),
                fontsize=font_size,
                color='white',  # Use white text for better contrast against dark background
                font=font_path if font_path else 'Arial',  # Use Arial as fallback
                method='caption',
                size=(width - 100, None),  # Leave margin
                align='center'
            )
            
            # Position text
            txt_clip = txt_clip.set_position(('center', y_position))
            
            # Apply animation
            txt_clip = self._apply_text_animation(
                txt_clip, animation_type, duration, i, len(poetry_lines)
            )
            
            text_clips.append(txt_clip)
            
        return text_clips
        
    def _apply_text_animation(
        self,
        txt_clip,
        animation_type: AnimationType,
        duration: int,
        line_index: int,
        total_lines: int
    ):
        """Apply animation to text clip."""
        if animation_type == AnimationType.FADE_IN:
            # Staggered fade in
            delay = line_index * 0.5
            txt_clip = txt_clip.set_start(delay).set_duration(duration - delay)
            txt_clip = txt_clip.fadein(1.0)
            
        elif animation_type == AnimationType.SLIDE_UP:
            # Slide up from bottom
            delay = line_index * 0.3
            txt_clip = txt_clip.set_start(delay).set_duration(duration - delay)
            
        elif animation_type == AnimationType.TYPEWRITER:
            # Simulate typewriter effect (simplified)
            delay = line_index * 0.8
            txt_clip = txt_clip.set_start(delay).set_duration(duration - delay)
            txt_clip = txt_clip.fadein(0.1)
            
        elif animation_type == AnimationType.WORD_BY_WORD:
            # Words appear one by one (simplified)
            delay = line_index * 0.6
            txt_clip = txt_clip.set_start(delay).set_duration(duration - delay)
            txt_clip = txt_clip.fadein(0.5)
            
        elif animation_type == AnimationType.GENTLE_ZOOM:
            # Gentle zoom and fade
            delay = line_index * 0.4
            txt_clip = txt_clip.set_start(delay).set_duration(duration - delay)
            txt_clip = txt_clip.fadein(0.8)
            
        else:
            # Default: simple fade in
            txt_clip = txt_clip.set_duration(duration).fadein(0.5)
            
        return txt_clip
        
    async def _get_background_video(
        self,
        theme_config: Dict[str, Any],
        theme_name: Optional[str],
        custom_background: Optional[str]
    ) -> Optional[str]:
        """Get background video file."""
        if custom_background:
            return await self._download_video(custom_background)
            
        # Use background service if available
        if self.background_service and theme_name:
            try:
                from config.themes import ThemeType
                # Convert theme name string to ThemeType enum
                theme_enum = None
                for theme in ThemeType:
                    if theme.value == theme_name:
                        theme_enum = theme
                        break
                
                if theme_enum:
                    logger.info(f"Using background service for theme: {theme_name}")
                    return await self.background_service.get_random_background(theme_enum)
                else:
                    logger.warning(f"Unknown theme: {theme_name}")
            except Exception as e:
                logger.warning(f"Failed to get background from service: {e}")
        
        # Fallback to local files
        backgrounds_dir = settings.backgrounds_dir
        if os.path.exists(backgrounds_dir):
            background_files = [
                f for f in os.listdir(backgrounds_dir)
                if f.lower().endswith(('.mp4', '.mov', '.avi'))
            ]
            if background_files:
                # Create temporary copy to avoid deleting original
                original_path = os.path.join(backgrounds_dir, random.choice(background_files))
                return await self._copy_to_temp(original_path)
                
        # If no backgrounds available, will use solid color
        return None
        
    async def _get_background_audio(
        self,
        theme_config: Dict[str, Any]
    ) -> Optional[str]:
        """Get background audio file."""
        # Use audio service if available
        if self.audio_service:
            try:
                return await self.audio_service.get_random_track()
            except Exception as e:
                logger.warning(f"Failed to get audio from service: {e}")
        
        # Fallback to local files
        audio_dir = settings.audio_dir
        if os.path.exists(audio_dir):
            audio_files = [
                f for f in os.listdir(audio_dir)
                if f.lower().endswith(('.mp3', '.wav', '.m4a'))
            ]
            if audio_files:
                # Create temporary copy to avoid deleting original
                original_path = os.path.join(audio_dir, random.choice(audio_files))
                return await self._copy_to_temp(original_path)
                
        return None
        
    async def _download_video(self, url: str) -> str:
        """Download video from URL to temporary file."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(
                    suffix='.mp4', delete=False
                ) as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return None
            
    async def _copy_to_temp(self, original_path: str) -> str:
        """Copy file to temporary location to avoid deleting original."""
        try:
            import shutil
            # Get file extension
            _, ext = os.path.splitext(original_path)
            
            # Create temporary file with same extension
            with tempfile.NamedTemporaryFile(
                suffix=ext, delete=False
            ) as tmp_file:
                temp_path = tmp_file.name
                
            # Copy original file to temp location
            shutil.copy2(original_path, temp_path)
            return temp_path
        except Exception as e:
            logger.error(f"Failed to copy file to temp: {e}")
            return original_path  # Return original as fallback
            
    def _get_font_path(self, font_family: str, text_style: TextStyle) -> str:
        """Get font path based on family and style."""
        # For now, use system defaults
        # In production, you'd have specific font files
        return None  # Let MoviePy use default
        
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def _parse_rgba(self, rgba_string: str) -> Tuple[int, ...]:
        """Parse RGBA string to tuple."""
        try:
            # Handle rgba(r, g, b, a) format
            if rgba_string.startswith('rgba('):
                values = rgba_string[5:-1].split(',')
                return tuple(float(v.strip()) for v in values)
            else:
                # Assume hex color
                return self._hex_to_rgb(rgba_string) + (1.0,)
        except Exception:
            return (0, 0, 0, 0.3) 