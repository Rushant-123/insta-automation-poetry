#!/usr/bin/env python3
"""
Script to convert trending poetry tracks to instrumental versions
Removes vocals to avoid competing with poetry narration
"""

import os
import subprocess
import sys
from pathlib import Path

# Audio directory
audio_dir = Path("audio")

def remove_vocals_from_track(input_path, output_path):
    """Remove vocals from an audio track using ffmpeg filters"""
    print(f"🎼 Converting to instrumental: {input_path.name}")
    
    try:
        # Method 1: Center channel extraction (removes most vocals)
        cmd = [
            "ffmpeg", 
            "-i", str(input_path),
            "-af", "pan=mono|c0=0.5*c0+-0.5*c1",  # Remove center channel (vocals)
            "-ac", "2",  # Convert back to stereo
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Method 1 success: {output_path.name}")
            return True
        else:
            print(f"⚠️  Method 1 failed, trying Method 2...")
            
            # Method 2: Vocal isolation and inversion
            cmd2 = [
                "ffmpeg", 
                "-i", str(input_path),
                "-af", "pan=stereo|c0=c0|c1=-1*c1",  # Invert right channel
                "-af", "pan=mono|c0=c0+c1",  # Mix to mono (cancels center)
                "-af", "pan=stereo|c0=c0|c1=c0",  # Back to stereo
                "-y",
                str(output_path)
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True)
            
            if result2.returncode == 0:
                print(f"✅ Method 2 success: {output_path.name}")
                return True
            else:
                print(f"⚠️  Method 2 failed, trying Method 3...")
                
                # Method 3: High-pass filter to reduce vocals
                cmd3 = [
                    "ffmpeg", 
                    "-i", str(input_path),
                    "-af", "highpass=f=200,lowpass=f=8000",  # Filter vocal frequencies
                    "-y",
                    str(output_path)
                ]
                
                result3 = subprocess.run(cmd3, capture_output=True, text=True)
                
                if result3.returncode == 0:
                    print(f"✅ Method 3 success: {output_path.name}")
                    return True
                else:
                    print(f"❌ All methods failed for: {input_path.name}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error processing {input_path.name}: {e}")
        return False

def process_all_tracks():
    """Convert all poetry tracks to instrumental versions"""
    print("🎼 Converting Poetry Tracks to Instrumental Versions")
    print("=" * 60)
    print("🎯 Removing vocals to avoid competing with poetry narration")
    
    # Find all trending poetry tracks
    track_files = list(audio_dir.glob("trending_poetry_*_30s.mp3"))
    
    if not track_files:
        print("❌ No trending poetry tracks found!")
        print("💡 Run python download_trending_poetry_audio.py first")
        return
    
    print(f"\n📁 Found {len(track_files)} tracks to convert")
    
    successful_conversions = 0
    
    for i, track_path in enumerate(track_files, 1):
        print(f"\n🎵 [{i}/{len(track_files)}] Processing: {track_path.name}")
        
        # Create instrumental filename
        instrumental_name = track_path.name.replace("_30s.mp3", "_instrumental_30s.mp3")
        instrumental_path = audio_dir / instrumental_name
        
        if remove_vocals_from_track(track_path, instrumental_path):
            successful_conversions += 1
            
            # Remove original vocal version to save space
            try:
                track_path.unlink()
                print(f"🗑️  Removed vocal version: {track_path.name}")
            except Exception as e:
                print(f"⚠️  Could not remove original: {e}")
        else:
            print(f"❌ Failed to convert: {track_path.name}")
    
    # Final summary
    print(f"\n🎉 Conversion Complete!")
    print(f"✅ Successfully converted: {successful_conversions}/{len(track_files)} tracks")
    
    # List instrumental files
    instrumental_files = list(audio_dir.glob("*_instrumental_30s.mp3"))
    print(f"\n📜 Instrumental Poetry Tracks Ready:")
    for i, file in enumerate(instrumental_files[:15], 1):
        print(f"{i:2d}. {file.name}")
    
    if len(instrumental_files) > 15:
        print(f"    ... and {len(instrumental_files) - 15} more")
    
    print(f"\n🎬 These instrumental tracks are perfect for poetry Reels!")
    print(f"📁 Location: {audio_dir.absolute()}")
    
    return successful_conversions

def main():
    if not audio_dir.exists():
        print("❌ Audio directory not found!")
        print("💡 Run python download_trending_poetry_audio.py first")
        return
    
    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found. Please install: brew install ffmpeg")
        return
    
    process_all_tracks()

if __name__ == "__main__":
    main() 