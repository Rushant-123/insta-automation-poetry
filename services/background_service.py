import os
import asyncio
import aiofiles
import httpx
import random
import logging
import tempfile
import shutil
from typing import List, Dict, Optional
from config.settings import settings
from config.themes import ThemeType

logger = logging.getLogger(__name__)


class BackgroundService:
    """Service for fetching and managing background videos."""
    
    def __init__(self):
        """Initialize background service."""
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', 'your_pexels_api_key_here')
        self.backgrounds_dir = settings.backgrounds_dir
        self.theme_keywords = {
            ThemeType.NATURE: ["leaves", "grass", "plants", "meadow", "flowers", "garden"],
            ThemeType.OCEAN: ["waves", "beach", "underwater", "sea", "water", "seascape"],
            ThemeType.SUNSET: ["sky", "clouds", "sunrise", "dawn", "dusk", "horizon"],
            ThemeType.FOREST: ["trees", "green", "woodland", "canopy", "branches", "foliage"],
            ThemeType.MINIMAL: ["geometric", "clean", "simple", "gradient", "smooth", "elegant"]
        }
        
    async def fetch_backgrounds_for_theme(
        self, 
        theme: ThemeType, 
        count: int = 5
    ) -> List[str]:
        """
        Fetch background videos for a specific theme.
        
        Args:
            theme: Theme type to fetch videos for
            count: Number of videos to fetch
            
        Returns:
            List of downloaded video file paths
        """
        logger.info(f"Fetching {count} background videos for theme: {theme}")
        
        keywords = self.theme_keywords.get(theme, ["nature"])
        downloaded_files = []
        
        try:
            # Try Pexels first
            pexels_files = await self._fetch_from_pexels(keywords, count)
            downloaded_files.extend(pexels_files)
            
            # If we don't have enough, try other sources
            if len(downloaded_files) < count:
                remaining = count - len(downloaded_files)
                pixabay_files = await self._fetch_from_pixabay(keywords, remaining)
                downloaded_files.extend(pixabay_files)
                
        except Exception as e:
            logger.error(f"Failed to fetch background videos: {e}")
            
        logger.info(f"Successfully downloaded {len(downloaded_files)} videos for {theme}")
        return downloaded_files
        
    async def _fetch_from_pexels(self, keywords: List[str], count: int) -> List[str]:
        """Fetch videos from Pexels API."""
        if self.pexels_api_key == 'your_pexels_api_key_here':
            logger.warning("Pexels API key not configured")
            return []
            
        downloaded_files = []
        
        async with httpx.AsyncClient() as client:
            for keyword in keywords[:2]:  # Use first 2 keywords
                try:
                    headers = {"Authorization": self.pexels_api_key}
                    params = {
                        "query": keyword,
                        "per_page": min(count, 15),
                        "size": "medium",
                        "orientation": "portrait"  # Better for Instagram
                    }
                    
                    response = await client.get(
                        "https://api.pexels.com/videos/search",
                        headers=headers,
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        videos = data.get("videos", [])
                        
                        for video in videos[:count//2]:
                            video_files = video.get("video_files", [])
                            # Get medium quality video
                            video_file = next(
                                (vf for vf in video_files if vf.get("quality") == "hd"),
                                video_files[0] if video_files else None
                            )
                            
                            if video_file:
                                video_url = video_file["link"]
                                filename = f"pexels_{keyword}_{video['id']}.mp4"
                                filepath = await self._download_video(video_url, filename)
                                if filepath:
                                    downloaded_files.append(filepath)
                                    
                    if len(downloaded_files) >= count:
                        break
                        
                except Exception as e:
                    logger.error(f"Failed to fetch from Pexels for keyword {keyword}: {e}")
                    
        return downloaded_files[:count]
        
    async def _fetch_from_pixabay(self, keywords: List[str], count: int) -> List[str]:
        """Fetch videos from Pixabay API (fallback)."""
        # Pixabay implementation would go here
        # For now, return empty list
        logger.info("Pixabay fetching not implemented yet")
        return []
        
    async def _download_video(self, url: str, filename: str) -> Optional[str]:
        """Download a video file."""
        try:
            filepath = os.path.join(self.backgrounds_dir, filename)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(response.content)
                    
            logger.info(f"Downloaded video: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to download video {filename}: {e}")
            return None
            
    async def get_random_background(self, theme: ThemeType) -> Optional[str]:
        """Get a random background video for theme."""
        theme_files = []
        
        # Check existing files first
        if os.path.exists(self.backgrounds_dir):
            all_files = [
                f for f in os.listdir(self.backgrounds_dir)
                if f.lower().endswith(('.mp4', '.mov', '.avi'))
            ]
            
            # Filter by theme if possible
            theme_keywords = [kw.lower() for kw in self.theme_keywords.get(theme, [])]
            theme_files = [
                f for f in all_files
                if any(keyword in f.lower() for keyword in theme_keywords)
            ]
            
            # If no theme-specific files, use any available
            if not theme_files:
                theme_files = all_files
                
        # If no files available, try to fetch one
        if not theme_files:
            logger.info(f"No background videos found for {theme}, fetching...")
            fetched = await self.fetch_backgrounds_for_theme(theme, 1)
            if fetched:
                return fetched[0]
            return None
            
        # Return random file as temporary copy
        selected_file = random.choice(theme_files)
        original_path = os.path.join(self.backgrounds_dir, selected_file)
        return await self._copy_to_temp(original_path)
        
    async def _copy_to_temp(self, original_path: str) -> str:
        """Copy background video to temporary location to avoid deleting original."""
        try:
            # Get file extension
            _, ext = os.path.splitext(original_path)
            
            # Create temporary file with same extension
            with tempfile.NamedTemporaryFile(
                suffix=ext, delete=False
            ) as tmp_file:
                temp_path = tmp_file.name
                
            # Copy original file to temp location
            shutil.copy2(original_path, temp_path)
            logger.info(f"Created temporary copy of background video: {os.path.basename(original_path)}")
            return temp_path
        except Exception as e:
            logger.error(f"Failed to copy background video to temp: {e}")
            return original_path  # Return original as fallback
        
    async def initialize_backgrounds(self):
        """Initialize background collection with 5 videos per theme."""
        logger.info("Initializing background video collection...")
        
        for theme in ThemeType:
            try:
                await self.fetch_backgrounds_for_theme(theme, 5)
            except Exception as e:
                logger.error(f"Failed to initialize backgrounds for {theme}: {e}")
                
        logger.info("Background initialization complete") 