#!/usr/bin/env python3
"""
Script to download popular instrumental music and trim to 45-second segments perfect for poetry Reels
"""

import os
import subprocess
import sys
from pathlib import Path
import time

# Ensure audio directory exists
audio_dir = Path("audio")
audio_dir.mkdir(exist_ok=True)

# Popular instrumental tracks that are trending and perfect for poetry Reels
POPULAR_INSTRUMENTALS = [
    # Lo-fi Hip Hop (Very Popular on Social Media)
    "Lofi Girl study beats",
    "ChilledCow lofi hip hop",
    "sad lofi hip hop beats",
    "aesthetic lofi playlist",
    
    # Popular Piano Instrumentals
    "Ludovico Einaudi Nuvole Bianche",
    "Yann Tiersen Comptine d'un autre été",
    "Max Richter On The Nature of Daylight", 
    "Ludovico Einaudi Una Mattina",
    "Ólafur Arnalds Near Light",
    
    # Trending Ambient/Electronic
    "Tycho A Walk",
    "Bonobo Kong",
    "Emancipator Soon It Will Be Cold Enough",
    "Boards of Canada Roygbiv",
    "Aphex Twin Avril 14th",
    
    # Popular Study/Focus Music
    "peaceful piano study music",
    "ambient focus music instrumental",
    "soft acoustic guitar instrumental",
    "chill instrumental beats",
    
    # Trending TikTok/Reels Instrumentals
    "aesthetic instrumental music",
    "dreamy instrumental playlist",
    "soft indie instrumental",
    "minimal piano emotional"
]

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found. Installing...")
        try:
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install ffmpeg. Please install manually: brew install ffmpeg")
            return False

def download_track(query, index, total):
    """Download a single track"""
    print(f"🎵 [{index}/{total}] Downloading: {query}")
    try:
        # Download to temporary filename
        temp_name = f"temp_{index}_{query.replace(' ', '_')[:30]}"
        
        cmd = [
            "spotdl", 
            "download", 
            query,
            "--output", str(audio_dir),
            "--format", "mp3",
            "--overwrite", "force"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ Downloaded: {query}")
            return True
        else:
            print(f"⚠️  Failed to download: {query}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout downloading: {query}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {query}: {e}")
        return False

def trim_to_45_seconds(file_path, output_path):
    """Trim audio file to best 45-second segment"""
    try:
        # Get file duration first
        duration_cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
            "-of", "csv=p=0", str(file_path)
        ]
        
        duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
        total_duration = float(duration_result.stdout.strip())
        
        # Calculate start time for best 45-second segment
        # Usually the best part is after the intro but before the outro
        if total_duration > 90:
            # For longer tracks, start after 25% and take 45 seconds
            start_time = total_duration * 0.25
        elif total_duration > 60:
            # For medium tracks, start after 20 seconds
            start_time = 20
        else:
            # For short tracks, start from beginning
            start_time = 0
        
        # Ensure we don't go past the end
        if start_time + 45 > total_duration:
            start_time = max(0, total_duration - 45)
        
        # Trim the audio
        trim_cmd = [
            "ffmpeg", "-i", str(file_path), 
            "-ss", str(start_time),
            "-t", "45",
            "-c", "copy",  # Copy without re-encoding for speed
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        result = subprocess.run(trim_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"⚠️  Trim failed, trying with re-encoding...")
            # Try again with re-encoding if copy failed
            trim_cmd = [
                "ffmpeg", "-i", str(file_path), 
                "-ss", str(start_time),
                "-t", "45",
                "-y", str(output_path)
            ]
            result = subprocess.run(trim_cmd, capture_output=True, text=True)
            return result.returncode == 0
            
    except Exception as e:
        print(f"❌ Error trimming {file_path}: {e}")
        return False

def process_downloaded_files():
    """Process all downloaded files to 45-second versions"""
    print("\n🎬 Processing files to 45-second segments...")
    
    # Find all mp3 files in audio directory
    mp3_files = list(audio_dir.glob("*.mp3"))
    
    processed_count = 0
    for i, file_path in enumerate(mp3_files, 1):
        print(f"✂️  [{i}/{len(mp3_files)}] Processing: {file_path.name}")
        
        # Create output filename
        output_name = f"poetry_reel_{i:02d}_{file_path.stem[:30]}_45s.mp3"
        output_path = audio_dir / output_name
        
        if trim_to_45_seconds(file_path, output_path):
            print(f"✅ Created: {output_name}")
            processed_count += 1
            
            # Remove original long file to save space
            try:
                file_path.unlink()
                print(f"🗑️  Removed original: {file_path.name}")
            except Exception as e:
                print(f"⚠️  Could not remove original: {e}")
        else:
            print(f"❌ Failed to process: {file_path.name}")
    
    return processed_count

def main():
    print("🎼 Popular Instrumental Music Downloader for Poetry Reels")
    print("=" * 60)
    print("📱 Downloads popular tracks and trims to perfect 45-second segments")
    
    # Check ffmpeg
    if not check_ffmpeg():
        return
    
    # Get user input for number of tracks
    try:
        max_tracks = input(f"\nHow many tracks to download? (1-{len(POPULAR_INSTRUMENTALS)}, default: 10): ").strip()
        max_tracks = int(max_tracks) if max_tracks else 10
        max_tracks = min(max_tracks, len(POPULAR_INSTRUMENTALS))
    except ValueError:
        max_tracks = 10
    
    print(f"\n🚀 Starting batch download of {max_tracks} popular instrumental tracks...")
    
    successful_downloads = 0
    tracks_to_download = POPULAR_INSTRUMENTALS[:max_tracks]
    
    # Batch download
    for i, track in enumerate(tracks_to_download, 1):
        if download_track(track, i, max_tracks):
            successful_downloads += 1
        
        # Small delay to be respectful to the API
        time.sleep(2)
    
    print(f"\n📊 Download Summary:")
    print(f"✅ Successfully downloaded: {successful_downloads}/{max_tracks} tracks")
    
    if successful_downloads > 0:
        # Process all downloaded files to 45-second segments
        processed_count = process_downloaded_files()
        
        # Final summary
        print(f"\n🎉 Final Results:")
        print(f"📁 Location: {audio_dir.absolute()}")
        print(f"✅ Processed tracks: {processed_count}")
        print(f"⏱️  Duration: 45 seconds each (perfect for Reels)")
        
        # List final files
        final_files = list(audio_dir.glob("poetry_reel_*.mp3"))
        print(f"\n📜 Ready-to-use poetry Reel tracks:")
        for i, file in enumerate(final_files[:15], 1):  # Show first 15
            print(f"{i:2d}. {file.name}")
        
        if len(final_files) > 15:
            print(f"    ... and {len(final_files) - 15} more")
            
        print(f"\n🎬 These tracks are now ready to use in your poetry Reel automation!")
    else:
        print("\n❌ No tracks were successfully downloaded.")

if __name__ == "__main__":
    main() 