import os
import asyncio
import random
import logging
import tempfile
import shutil
from typing import List, Dict, Optional
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Service for managing local poetry Reel music tracks."""
    
    def __init__(self):
        """Initialize audio service with local track management."""
        self.audio_dir = Path(settings.audio_dir)
        self.local_tracks = self._discover_local_tracks()
        
        # Ensure audio directory exists
        os.makedirs(self.audio_dir, exist_ok=True)
        
        logger.info(f"Audio service initialized with {len(self.local_tracks)} local tracks")
        
    def _discover_local_tracks(self) -> List[str]:
        """Discover all available local audio tracks."""
        if not self.audio_dir.exists():
            return []
            
        # Look for our tracks in priority order
        tracks = []
        
        # HIGHEST Priority: Trending poetry instrumental tracks (perfect!)
        trending_instrumental = list(self.audio_dir.glob("trending_poetry_*_instrumental_30s.mp3"))
        tracks.extend([str(track) for track in trending_instrumental])
        
        # Medium Priority: Other poetry reel tracks (45-second, perfectly trimmed)
        poetry_tracks = list(self.audio_dir.glob("poetry_reel_*_45s.mp3"))
        poetry_tracks = [f for f in poetry_tracks if str(f) not in tracks]  # Avoid duplicates
        tracks.extend([str(track) for track in poetry_tracks])
        
        # Low Priority: Any other audio files
        other_audio = list(self.audio_dir.glob("*.mp3")) + list(self.audio_dir.glob("*.wav"))
        other_audio = [f for f in other_audio if str(f) not in tracks]  # Avoid duplicates
        tracks.extend([str(track) for track in other_audio])
        
        logger.info(f"Discovered {len(trending_instrumental)} trending instrumental tracks, {len(poetry_tracks)} poetry reel tracks, and {len(other_audio)} other tracks")
        return tracks
    
    async def fetch_peaceful_music(self, count: int = 10) -> List[str]:
        """
        Get paths to local peaceful music tracks for poetry videos.
        
        Returns:
            List of file paths to audio tracks
        """
        try:
            if not self.local_tracks:
                logger.warning("No local audio tracks found!")
                return []
            
            # Categorize tracks by priority for poetry content
            trending_instrumental = [t for t in self.local_tracks if "trending_poetry_" in t and "_instrumental_30s.mp3" in t]
            poetry_tracks = [t for t in self.local_tracks if "poetry_reel_" in t and "_45s.mp3" in t]
            other_tracks = [t for t in self.local_tracks if t not in trending_instrumental and t not in poetry_tracks]
            
            selected_tracks = []
            
            # First priority: Trending instrumental tracks (BEST for poetry!)
            if trending_instrumental:
                needed = min(count, len(trending_instrumental))
                selected_instrumental = random.sample(trending_instrumental, needed)
                selected_tracks.extend(selected_instrumental)
                logger.info(f"Selected {len(selected_instrumental)} trending instrumental tracks")
            
            # Second priority: Poetry reel tracks if we need more
            remaining_needed = count - len(selected_tracks)
            if remaining_needed > 0 and poetry_tracks:
                needed = min(remaining_needed, len(poetry_tracks))
                selected_poetry = random.sample(poetry_tracks, needed)
                selected_tracks.extend(selected_poetry)
                logger.info(f"Added {len(selected_poetry)} poetry reel tracks")
            
            # Third priority: Other tracks if still need more
            remaining_needed = count - len(selected_tracks)
            if remaining_needed > 0 and other_tracks:
                needed = min(remaining_needed, len(other_tracks))
                selected_other = random.sample(other_tracks, needed)
                selected_tracks.extend(selected_other)
                logger.info(f"Added {len(selected_other)} additional tracks")
            
            # Shuffle for variety within the same priority level
            random.shuffle(selected_tracks)
            
            logger.info(f"Returning {len(selected_tracks)} audio tracks for poetry videos (prioritizing instrumental)")
            return selected_tracks[:count]
            
        except Exception as e:
            logger.error(f"Failed to fetch local music: {e}")
            return []
    
    async def get_random_track(self) -> Optional[str]:
        """Get a single random track for a poetry video."""
        tracks = await self.fetch_peaceful_music(count=1)
        if tracks:
            # Create temporary copy to avoid deleting original
            return await self._copy_to_temp(tracks[0])
        return None
    
    async def _copy_to_temp(self, original_path: str) -> str:
        """Copy audio file to temporary location to avoid deleting original."""
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
            logger.info(f"Created temporary copy of audio file: {os.path.basename(original_path)}")
            return temp_path
        except Exception as e:
            logger.error(f"Failed to copy audio file to temp: {e}")
            return original_path  # Return original as fallback
    
    def get_track_info(self, track_path: str) -> Dict:
        """Get information about a track."""
        path = Path(track_path)
        filename = path.name
        
        # Determine track type and duration
        is_trending_instrumental = "trending_poetry_" in filename and "_instrumental_30s" in filename
        is_poetry_reel = "poetry_reel_" in filename and "_45s" in filename
        is_instrumental = "_instrumental_" in filename
        
        # Extract mood/type from trending tracks
        track_mood = "Unknown"
        if is_trending_instrumental:
            # Map some known tracks to their moods
            if "Indila - Love Story" in filename:
                track_mood = "Lush, melancholic build; heartbreak, growth arcs"
            elif "Commodores - Easy" in filename:
                track_mood = "Soft retro soul; self-acceptance"
            elif "Men I Trust" in filename:
                track_mood = "Cozy introspection; quiet-day poems"
            elif "Doechii - Anxiety" in filename:
                track_mood = "Mental health spoken pieces; tension/release"
            elif "Jazz Coffeehouse" in filename:
                track_mood = "Warm coffeehouse spoken word; intimate readings"
            elif "Urban jon - Moments" in filename:
                track_mood = "Nostalgia poems; memory flashbacks; travel haiku"
            else:
                track_mood = "Trending poetry-optimized audio"
        
        return {
            "filename": filename,
            "path": str(path),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else 0,
            "is_trending_instrumental": is_trending_instrumental,
            "is_poetry_reel": is_poetry_reel,
            "is_instrumental": is_instrumental,
            "estimated_duration": "30 seconds" if "_30s" in filename else "45 seconds" if "_45s" in filename else "unknown",
            "track_mood": track_mood,
            "priority": "highest" if is_trending_instrumental else "medium" if is_poetry_reel else "low"
        }
    
    def get_all_tracks_info(self) -> List[Dict]:
        """Get information about all available tracks."""
        return [self.get_track_info(track) for track in self.local_tracks]
    
    def refresh_tracks(self):
        """Refresh the list of available local tracks."""
        self.local_tracks = self._discover_local_tracks()
        logger.info(f"Refreshed track list: {len(self.local_tracks)} tracks available")
    
    # Keep these for compatibility with existing endpoints
    async def test_apis(self) -> Dict[str, bool]:
        """Test if local audio system is working."""
        return {
            "local_audio": len(self.local_tracks) > 0,
            "poetry_reels_available": any("poetry_reel_" in track for track in self.local_tracks)
        }
    
    def get_api_status_summary(self) -> str:
        """Get a summary of the audio system status."""
        trending_count = sum(1 for track in self.local_tracks if "trending_poetry_" in track and "_instrumental_30s" in track)
        poetry_count = sum(1 for track in self.local_tracks if "poetry_reel_" in track)
        total_count = len(self.local_tracks)
        
        if trending_count > 0:
            return f"🔥 {trending_count} trending instrumental tracks ready + {poetry_count} poetry reels + {total_count - trending_count - poetry_count} others"
        elif poetry_count > 0:
            return f"✅ {poetry_count} poetry reel tracks ready + {total_count - poetry_count} other tracks"
        elif total_count > 0:
            return f"⚠️  {total_count} audio tracks available (no poetry-optimized tracks)"
        else:
            return "❌ No audio tracks found"
    
    def get_setup_instructions(self) -> Dict:
        """Get setup instructions for the audio system."""
        trending_count = sum(1 for track in self.local_tracks if "trending_poetry_" in track and "_instrumental_30s" in track)
        poetry_count = sum(1 for track in self.local_tracks if "poetry_reel_" in track)
        
        return {
            "status": "ready" if self.local_tracks else "no_tracks",
            "trending_instrumental_count": trending_count,
            "poetry_reel_count": poetry_count,
            "total_tracks": len(self.local_tracks),
            "instructions": {
                "current_setup": "Using local audio tracks for poetry videos",
                "trending_instrumental": f"{trending_count} trending poetry-friendly instrumental tracks (30s, no vocals)",
                "poetry_reel_tracks": f"{poetry_count} poetry reel tracks (45s, instrumental)",
                "location": str(self.audio_dir),
                "priority_order": "1. Trending instrumental (highest) → 2. Poetry reels (medium) → 3. Others (low)",
                "to_add_more": {
                    "trending": "Run python download_trending_poetry_audio.py to download more trending tracks",
                    "convert_to_instrumental": "Run python convert_to_instrumental.py to remove vocals",
                    "classic_instrumental": "Run python download_music.py for classic instrumental tracks"
                }
            },
            "files": [self.get_track_info(track) for track in self.local_tracks[:10]]  # Show first 10
        } 