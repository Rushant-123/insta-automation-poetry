#!/usr/bin/env python3
"""
Script to download soft instrumental music from Spotify playlist for poetry videos
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure audio directory exists
audio_dir = Path("audio")
audio_dir.mkdir(exist_ok=True)

# Soft Instrumental Music Playlist (July 2025)
SPOTIFY_POETRY_AUDIOS = [
    {
        "id": 1,
        "track": "Circle of Life",
        "artist": "Soulgarden",
        "searchable": "Soulgarden Circle of Life instrumental",
        "mood": "Peaceful, contemplative; nature themes",
        "type": "spotify_instrumental"
    },
    {
        "id": 2,
        "track": "Susurros de Eternidad",
        "artist": "Sveria",
        "searchable": "Sveria Susurros de Eternidad",
        "mood": "Ethereal, mystical; spiritual reflection",
        "type": "spotify_instrumental"
    },
    {
        "id": 3,
        "track": "Near to Me",
        "artist": "Simon Wester, Dear Gravity",
        "searchable": "Simon Wester Dear Gravity Near to Me",
        "mood": "Intimate, personal; relationship poems",
        "type": "spotify_instrumental"
    },
    {
        "id": 4,
        "track": "Variations Of Chill",
        "artist": "Lennie Rhoads, Pacific Strings",
        "searchable": "Lennie Rhoads Pacific Strings Variations Of Chill",
        "mood": "Relaxed, flowing; meditative verses",
        "type": "spotify_instrumental"
    },
    {
        "id": 5,
        "track": "Äntligen Lugnt",
        "artist": "Eric Rohr, David Peter Vestin",
        "searchable": "Eric Rohr David Peter Vestin Antligen Lugnt",
        "mood": "Serene, calming; mindfulness poems",
        "type": "spotify_instrumental"
    },
    {
        "id": 6,
        "track": "Nimbus",
        "artist": "Howard Skybrooke",
        "searchable": "Howard Skybrooke Nimbus",
        "mood": "Atmospheric, dreamy; cloud imagery",
        "type": "spotify_instrumental"
    },
    {
        "id": 7,
        "track": "139th Street",
        "artist": "Pommes Cannelle",
        "searchable": "Pommes Cannelle 139th Street",
        "mood": "Urban peace; city life reflections",
        "type": "spotify_instrumental"
    },
    {
        "id": 8,
        "track": "Grateful",
        "artist": "Nylonwings",
        "searchable": "Nylonwings Grateful",
        "mood": "Thankful, uplifting; gratitude poems",
        "type": "spotify_instrumental"
    },
    {
        "id": 9,
        "track": "Blommor",
        "artist": "Dientes de León",
        "searchable": "Dientes de Leon Blommor",
        "mood": "Gentle growth; nature's cycles",
        "type": "spotify_instrumental"
    },
    {
        "id": 10,
        "track": "Universe in me",
        "artist": "Soulgarden",
        "searchable": "Soulgarden Universe in me",
        "mood": "Cosmic wonder; existential themes",
        "type": "spotify_instrumental"
    },
    {
        "id": 11,
        "track": "Days in Valencia",
        "artist": "Northern Sunrise",
        "searchable": "Northern Sunrise Days in Valencia",
        "mood": "Mediterranean warmth; travel poems",
        "type": "spotify_instrumental"
    },
    {
        "id": 12,
        "track": "Winding Time",
        "artist": "Furari",
        "searchable": "Furari Winding Time",
        "mood": "Time's passage; life journey verses",
        "type": "spotify_instrumental"
    }
]

def check_spotdl():
    """Check if spotdl is installed"""
    try:
        subprocess.run(["spotdl", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ spotdl not found. Installing...")
        try:
            subprocess.run(["pip", "install", "spotdl"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install spotdl. Please install manually: pip install spotdl")
            return False

def download_poetry_track(track_info, index, total):
    """Download a single poetry track"""
    track_name = track_info["track"]
    artist = track_info["artist"]
    search_query = track_info["searchable"]
    
    print(f"🎵 [{index}/{total}] Downloading: {track_name} by {artist}")
    print(f"    🎭 Mood: {track_info['mood']}")
    
    try:
        cmd = [
            "spotdl", 
            "download", 
            search_query,
            "--output", str(audio_dir),
            "--format", "mp3",
            "--overwrite", "force"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Downloaded: {track_name}")
            return True
        else:
            print(f"❌ Failed to download: {track_name}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout downloading: {track_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {track_name}: {e}")
        return False

def trim_tracks_to_30_seconds():
    """Trim all downloaded tracks to 30-second segments perfect for poetry videos"""
    print("\n🎬 Processing tracks to 30-second poetry segments...")
    
    mp3_files = list(audio_dir.glob("*.mp3"))
    
    if not mp3_files:
        print("❌ No audio files found to process!")
        return 0
    
    processed_count = 0
    for i, file_path in enumerate(mp3_files, 1):
        print(f"✂️  [{i}/{len(mp3_files)}] Processing: {file_path.name}")
        
        # Create output filename for slow poetry tracks
        output_name = f"slow_poetry_{i:02d}_{file_path.stem[:30]}_instrumental_30s.mp3"
        output_path = audio_dir / output_name
        
        try:
            # Get file duration
            duration_cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
                "-of", "csv=p=0", str(file_path)
            ]
            
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            total_duration = float(duration_result.stdout.strip())
            
            # Calculate start time for best 30-second segment
            if total_duration > 90:
                # For longer tracks, start after 25% for the melodic section
                start_time = total_duration * 0.25
            elif total_duration > 45:
                # For medium tracks, start after intro
                start_time = 15
            else:
                # For short tracks, start from beginning
                start_time = 0
            
            # Ensure we don't go past the end
            if start_time + 30 > total_duration:
                start_time = max(0, total_duration - 30)
            
            # Trim the audio to 30 seconds
            trim_cmd = [
                "ffmpeg", "-i", str(file_path), 
                "-ss", str(start_time),
                "-t", "30",
                "-c", "copy",
                "-y", str(output_path)
            ]
            
            subprocess.run(trim_cmd, check=True, capture_output=True)
            print(f"✅ Created: {output_name}")
            processed_count += 1
            
            # Remove original file to save space
            try:
                file_path.unlink()
                print(f"🗑️  Removed original: {file_path.name}")
            except Exception as e:
                print(f"⚠️  Could not remove original: {e}")
                
        except Exception as e:
            print(f"❌ Failed to process {file_path.name}: {e}")
            
    return processed_count

def main():
    """Main execution flow"""
    print("🎵 Poetry Video Background Music Downloader")
    print("=" * 50)
    
    if not check_spotdl():
        sys.exit(1)
    
    # Download tracks
    print("\n📥 Downloading tracks from Spotify...")
    successful_downloads = 0
    
    for i, track in enumerate(SPOTIFY_POETRY_AUDIOS, 1):
        if download_poetry_track(track, i, len(SPOTIFY_POETRY_AUDIOS)):
            successful_downloads += 1
            
        # Small delay between downloads
        time.sleep(2)
    
    if successful_downloads == 0:
        print("\n❌ No tracks were downloaded successfully!")
        sys.exit(1)
    
    # Process downloaded tracks
    print(f"\n✨ Successfully downloaded {successful_downloads} tracks")
    processed_count = trim_tracks_to_30_seconds()
    
    print(f"\n🎉 All done! {processed_count} tracks ready for poetry videos")
    print("📁 Check the audio/ directory for the processed files")

if __name__ == "__main__":
    main() 