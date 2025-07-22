import os
import asyncio
import tempfile
import logging
from typing import List, Optional, Dict
import subprocess
from pathlib import Path
import re
import aiohttp
import json

from config.settings import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Service for generating text-to-speech voice-over for poetry."""
    
    def __init__(self):
        """Initialize TTS service."""
        self.tts_dir = Path("audio/tts")
        self.tts_dir.mkdir(parents=True, exist_ok=True)
        self.available_voices = self._get_available_voices()
        
        # Azure OpenAI TTS configuration (separate from GPT)
        self.azure_endpoint = os.getenv("AZURE_OPENAI_TTS_ENDPOINT", "https://dunlin-deployment.openai.azure.com/")
        self.azure_api_key = os.getenv("AZURE_OPENAI_TTS_API_KEY", "EqxJDSX9qYv3w0C0kixWm1EtjKNlFO7v3a3TRKvZTjiNFVhFWDgjJQQJ99ALACHrzpqXJ3w3AAABACOGYMAg")
        self.azure_api_version = os.getenv("AZURE_OPENAI_TTS_API_VERSION", "2025-03-01-preview")
        self.azure_deployment_name = "tts-hd"  # Use the correct deployment name from JS example
        
    def _get_available_voices(self) -> Dict[str, str]:
        """Get available voices for different TTS engines."""
        voices = {
            # Azure OpenAI TTS voices (premium quality)
            "azure_onyx": "onyx",
            "azure_alloy": "alloy",
            "azure_echo": "echo",
            "azure_fable": "fable",
            "azure_nova": "nova",
            "azure_shimmer": "shimmer",
            
            # Microsoft Edge TTS voices (high quality)
            "edge_female_calm": "en-US-AriaNeural",
            "edge_female_warm": "en-US-JennyNeural", 
            "edge_male_calm": "en-US-DavisNeural",
            "edge_male_warm": "en-US-GuyNeural",
            "edge_female_british": "en-GB-SoniaNeural",
            "edge_male_british": "en-GB-RyanNeural",
            
            # System voices (fallback)
            "system_female": "com.apple.voice.compact.en-US.Samantha",
            "system_male": "com.apple.voice.compact.en-US.Alex"
        }
        return voices
        
    async def generate_poetry_voiceover(
        self,
        poetry_lines: List[str],
        voice_style: str = "edge_female_calm",
        speaking_rate: float = 0.7,
        pause_between_lines: float = 0.8
    ) -> str:
        """
        Generate voice-over for poetry lines.
        
        Args:
            poetry_lines: List of poetry lines to speak
            voice_style: Voice style to use
            speaking_rate: Speaking rate (0.5-2.0)
            pause_between_lines: Pause between lines in seconds
            
        Returns:
            Path to generated audio file
        """
        try:
            # Clean and prepare text
            cleaned_lines = self._clean_poetry_text(poetry_lines)
            full_text = self._format_poetry_for_speech(cleaned_lines, pause_between_lines)
            
            # Generate unique filename
            text_hash = hash(full_text + voice_style)
            output_file = self.tts_dir / f"poetry_voiceover_{abs(text_hash)}.wav"
            
            # Check if already generated
            if output_file.exists():
                logger.info(f"Using cached voice-over: {output_file.name}")
                return str(output_file)
            
            # Try different TTS engines in order of preference
            success = False
            
            # Try Azure OpenAI TTS first (premium quality)
            if voice_style.startswith("azure_"):
                success = await self._generate_azure_tts(full_text, output_file, voice_style, speaking_rate)
            
            # Try Microsoft Edge TTS (high quality)
            if not success and voice_style.startswith("edge_"):
                success = await self._generate_edge_tts(full_text, output_file, voice_style, speaking_rate)
                
            # Fallback to system TTS
            if not success:
                success = await self._generate_system_tts(full_text, output_file, voice_style, speaking_rate)
                
            # Final fallback to basic TTS
            if not success:
                success = await self._generate_basic_tts(full_text, output_file, speaking_rate)
                
            if success and output_file.exists():
                logger.info(f"Generated voice-over: {output_file.name}")
                return str(output_file)
            else:
                logger.error("All TTS methods failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate voice-over: {e}")
            return None
    
    def _clean_poetry_text(self, poetry_lines: List[str]) -> List[str]:
        """Clean poetry text for better speech synthesis."""
        cleaned = []
        for line in poetry_lines:
            # Remove extra whitespace
            line = line.strip()
            if not line:
                continue
                
            # Handle common poetry punctuation
            line = re.sub(r'--+', ' - ', line)  # Replace dashes
            line = re.sub(r'\.{3,}', '...', line)  # Normalize ellipsis
            line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
            
            cleaned.append(line)
        return cleaned
    
    def _format_poetry_for_speech(self, lines: List[str], pause_between_lines: float) -> str:
        """Format poetry for natural speech synthesis."""
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # Add natural pauses using SSML-like syntax
            if i > 0:
                # Add pause between lines
                pause_ms = int(pause_between_lines * 1000)
                formatted_lines.append(f"<break time='{pause_ms}ms'/>")
            
            # Add pauses around punctuation for better poetry rhythm
            line_with_pauses = line
            # Add longer pause after full stops and question marks
            line_with_pauses = re.sub(r'([.!?])', r'\1<break time="600ms"/>', line_with_pauses)
            # Add medium pause after commas and semicolons
            line_with_pauses = re.sub(r'([,;])', r'\1<break time="400ms"/>', line_with_pauses)
            # Add short pause after colons
            line_with_pauses = re.sub(r'([:])', r'\1<break time="300ms"/>', line_with_pauses)
            
            formatted_lines.append(line_with_pauses)
        
        return " ".join(formatted_lines)
    
    async def _generate_azure_tts(self, text: str, output_file: Path, voice_style: str, speaking_rate: float) -> bool:
        """Generate TTS using Azure OpenAI TTS."""
        try:
            # Clean text for Azure OpenAI (remove SSML tags)
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Get voice model
            voice_model = self.available_voices.get(voice_style, "onyx")
            
            # Prepare Azure OpenAI TTS request
            url = f"{self.azure_endpoint.rstrip('/')}/openai/deployments/{self.azure_deployment_name}/audio/speech"
            
            headers = {
                "Authorization": f"Bearer {self.azure_api_key}",  # Use Bearer token format like JS example
                "Content-Type": "application/json"
            }
            
            # Convert speaking rate to speed (Azure OpenAI expects 0.25-4.0)
            speed = max(0.25, min(4.0, speaking_rate))
            
            data = {
                "model": "tts-hd",  # Use the same model as deployment name like JS example
                "input": clean_text,
                "voice": voice_model,
                "speed": speed,
                "response_format": "wav"
            }
            
            # Add API version as query parameter
            params = {
                "api-version": self.azure_api_version
            }
            
            # Make async request to Azure OpenAI
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, params=params, timeout=60) as response:
                    if response.status == 200:
                        # Save audio data to file
                        with open(output_file, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        if output_file.exists() and output_file.stat().st_size > 0:
                            logger.info(f"Generated voice-over with Azure OpenAI TTS: {voice_model}")
                            return True
                        else:
                            logger.warning("Azure OpenAI TTS returned empty file")
                            return False
                    else:
                        error_text = await response.text()
                        logger.warning(f"Azure OpenAI TTS failed with status {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.warning(f"Azure OpenAI TTS failed: {e}")
            return False
    
    async def _generate_edge_tts(self, text: str, output_file: Path, voice_style: str, speaking_rate: float) -> bool:
        """Generate TTS using Microsoft Edge TTS."""
        try:
            # Check if edge-tts is available
            result = subprocess.run(["edge-tts", "--help"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("edge-tts not available, trying to install...")
                subprocess.run(["pip", "install", "edge-tts"], check=True)
            
            voice_name = self.available_voices.get(voice_style, "en-US-AriaNeural")
            
            # Clean text for edge-tts (remove SSML for now)
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Generate with edge-tts
            # Convert speaking rate to proper format (e.g., "+20%" or "-20%")
            rate_percent = int((speaking_rate - 1.0) * 100)
            rate_str = f"{rate_percent:+d}%" if rate_percent != 0 else "+0%"
            
            cmd = [
                "edge-tts",
                "--voice", voice_name,
                f"--rate={rate_str}",  # Use equals format to prevent argument splitting
                "--text", clean_text,
                "--write-media", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Generated voice-over with edge-tts: {voice_name}")
                return True
            else:
                logger.warning(f"Edge TTS failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return False
    
    async def _generate_system_tts(self, text: str, output_file: Path, voice_style: str, speaking_rate: float) -> bool:
        """Generate TTS using system voice (macOS)."""
        try:
            # Clean text
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Use macOS say command
            voice_name = self.available_voices.get(voice_style, "Samantha")
            
            cmd = [
                "say",
                "-v", voice_name.split('.')[-1] if '.' in voice_name else voice_name,  # Extract voice name
                "-r", str(int(speaking_rate * 200)),  # Convert to words per minute
                "-o", str(output_file.with_suffix('.aiff')),  # Use AIFF format for say command
                clean_text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Convert AIFF to WAV if successful
            if result.returncode == 0:
                aiff_file = output_file.with_suffix('.aiff')
                if aiff_file.exists():
                    # Convert to WAV using ffmpeg
                    convert_cmd = ["ffmpeg", "-i", str(aiff_file), "-y", str(output_file)]
                    convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                    
                    # Clean up AIFF file
                    try:
                        aiff_file.unlink()
                    except:
                        pass
                    
                    # Check if conversion was successful
                    if convert_result.returncode == 0 and output_file.exists():
                        logger.info(f"Generated voice-over with system TTS: {voice_name}")
                        return True
            
            if result.returncode == 0 and output_file.exists():
                logger.info(f"Generated voice-over with system TTS: {voice_name}")
                return True
            else:
                logger.warning(f"System TTS failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.warning(f"System TTS failed: {e}")
            return False
    
    async def _generate_basic_tts(self, text: str, output_file: Path, speaking_rate: float) -> bool:
        """Generate TTS using basic Python TTS as last resort."""
        try:
            # Clean text
            clean_text = re.sub(r'<[^>]+>', '', text)
            
            # Try using macOS 'say' command directly as fallback
            cmd = [
                "say",
                "-r", str(int(speaking_rate * 200)),
                "-o", str(output_file.with_suffix('.aiff')),
                clean_text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                aiff_file = output_file.with_suffix('.aiff')
                if aiff_file.exists():
                    # Convert to WAV
                    convert_cmd = ["ffmpeg", "-i", str(aiff_file), "-y", str(output_file)]
                    convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                    
                    # Clean up
                    try:
                        aiff_file.unlink()
                    except:
                        pass
                    
                    if convert_result.returncode == 0 and output_file.exists():
                        logger.info("Generated voice-over with basic TTS")
                        return True
            
            return False
                
        except Exception as e:
            logger.warning(f"Basic TTS failed: {e}")
            return False
    
    async def get_voice_options(self) -> Dict[str, Dict[str, str]]:
        """Get available voice options for UI."""
        return {
            "azure_onyx": {
                "name": "Onyx (Premium Male)",
                "description": "Deep, rich male voice with exceptional clarity - Azure OpenAI premium",
                "language": "en-US",
                "quality": "premium"
            },
            "azure_alloy": {
                "name": "Alloy (Balanced Neutral)",
                "description": "Balanced, versatile voice suitable for all content - Azure OpenAI",
                "language": "en-US",
                "quality": "premium"
            },
            "azure_echo": {
                "name": "Echo (Resonant Male)",
                "description": "Clear, resonant male voice with excellent articulation - Azure OpenAI",
                "language": "en-US",
                "quality": "premium"
            },
            "azure_fable": {
                "name": "Fable (Warm Narrator)",
                "description": "Warm, storytelling voice perfect for poetry - Azure OpenAI",
                "language": "en-US",
                "quality": "premium"
            },
            "azure_nova": {
                "name": "Nova (Bright Female)",
                "description": "Bright, energetic female voice with clear pronunciation - Azure OpenAI",
                "language": "en-US",
                "quality": "premium"
            },
            "azure_shimmer": {
                "name": "Shimmer (Gentle Female)",
                "description": "Soft, gentle female voice ideal for poetry - Azure OpenAI",
                "language": "en-US",
                "quality": "premium"
            },
            "edge_female_calm": {
                "name": "Aria (Calm Female)",
                "description": "Gentle, soothing female voice perfect for poetry",
                "language": "en-US",
                "quality": "high"
            },
            "edge_female_warm": {
                "name": "Jenny (Warm Female)", 
                "description": "Warm, expressive female voice",
                "language": "en-US",
                "quality": "high"
            },
            "edge_male_calm": {
                "name": "Davis (Calm Male)",
                "description": "Gentle, thoughtful male voice",
                "language": "en-US", 
                "quality": "high"
            },
            "edge_female_british": {
                "name": "Sonia (British Female)",
                "description": "Elegant British accent",
                "language": "en-GB",
                "quality": "high"
            }
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old TTS files to save space."""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.tts_dir.glob("*.wav"):
                if current_time - file_path.stat().st_mtime > max_age_hours * 3600:
                    file_path.unlink()
                    logger.info(f"Cleaned up old TTS file: {file_path.name}")
                    
        except Exception as e:
            logger.warning(f"Failed to cleanup TTS files: {e}") 