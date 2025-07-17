#!/usr/bin/env python3
"""
Script to download slow, relaxed, smooth instrumental tracks perfect for poetry
Focuses on contemplative, reflective audio that complements spoken word
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure audio directory exists
audio_dir = Path("audio")
audio_dir.mkdir(exist_ok=True)

# 20 Slow / Relaxed / Smooth Reel Audios for Poetry (July 2025)
SLOW_POETRY_AUDIOS = [
    {
        "id": 1,
        "track": "Love Story - Indila",
        "searchable": "Indila Love Story instrumental",
        "mood": "Cinematic melancholy; heartbreak, metamorphosis, reflective arcs",
        "type": "spotify_instrumental",
        "why_good": "Currently resurging in slow, emotive storytelling edits"
    },
    {
        "id": 2,
        "track": "Moments - Urban Jon",
        "searchable": "Urban Jon Moments instrumental",
        "mood": "Soft reflective bed; memory collage, travel haiku, nostalgia prose",
        "type": "spotify_instrumental",
        "why_good": "Calm + reflective and used for montage storytelling"
    },
    {
        "id": 3,
        "track": "Enjoy the Moment - Kael Drakon",
        "searchable": "Kael Drakon Enjoy the Moment instrumental",
        "mood": "Gentle uplift; gratitude poems, morning journaling reels",
        "type": "spotify_instrumental",
        "why_good": "Breezy vibe trending under everyday-joy / slow aesthetic videos"
    },
    {
        "id": 4,
        "track": "Praia Beach - Dih",
        "searchable": "Dih Praia Beach instrumental",
        "mood": "Chill instrumental sea-breeze; stillness, breath, nature metaphors",
        "type": "spotify_instrumental",
        "why_good": "Relaxed, escapist vibe—great tranquil mood setter"
    },
    {
        "id": 5,
        "track": "Over and Over - Adam Griffith",
        "searchable": "Adam Griffith Over and Over instrumental",
        "mood": "Ambient / cinematic swell; contemplative long-form text overlays",
        "type": "spotify_instrumental",
        "why_good": "Recommended for slow, detail-appreciation and process visuals"
    },
    {
        "id": 6,
        "track": "Heaven - Original Audio",
        "searchable": "ethereal heaven ambient instrumental piano",
        "mood": "Ethereal + airy; floaty bliss poems, spiritual lines, gratitude montages",
        "type": "ambient_search",
        "why_good": "Calming / serene usage; perfect for spiritual content"
    },
    {
        "id": 7,
        "track": "I Have Everything I Need - Original Audio",
        "searchable": "contentment gratitude minimalism instrumental",
        "mood": "Contentment mantra; minimalism poems, things that matter lists",
        "type": "ambient_search",
        "why_good": "Trending for essentials-style storytelling"
    },
    {
        "id": 8,
        "track": "Easy - Commodores",
        "searchable": "Commodores Easy instrumental",
        "mood": "Classic laid-back soul; self-acceptance, slow Sunday verse",
        "type": "spotify_instrumental",
        "why_good": "Relaxed mood track perfect for self-acceptance themes"
    },
    {
        "id": 9,
        "track": "A Narrated Life - Faye Webster",
        "searchable": "Faye Webster A Narrated Life instrumental",
        "mood": "Gentle indie narration feel; life-in-third-person poems",
        "type": "spotify_instrumental",
        "why_good": "Works for soft POV storytelling"
    },
    {
        "id": 10,
        "track": "I Grieve Different - Original Audio",
        "searchable": "tender grief healing piano instrumental",
        "mood": "Tender, introspective; healing poems, grief to growth arcs",
        "type": "ambient_search",
        "why_good": "Perfect for reflective storytelling and emotional healing"
    },
    {
        "id": 11,
        "track": "Something to Take the Edge Off - Original Audio",
        "searchable": "calming comfort soothing instrumental",
        "mood": "Chill decompress; what soothes me poems, coping mantras",
        "type": "ambient_search",
        "why_good": "Used to show calming rituals / comfort objects"
    },
    {
        "id": 12,
        "track": "Be Your Girl - Original Audio",
        "searchable": "laidback chill loop instrumental",
        "mood": "Laidback vibey loop; soft confessional poetry, crush pieces",
        "type": "ambient_search",
        "why_good": "Chilled, flexible format—good for low-energy edits"
    },
    {
        "id": 13,
        "track": "Hmm Hmm Hmm - Original Audio",
        "searchable": "minimal peaceful meditation instrumental",
        "mood": "Minimal hum / inner peace; breath poems, micro-meditations",
        "type": "ambient_search",
        "why_good": "If inner peace had a sound usage cue"
    },
    {
        "id": 14,
        "track": "Deep In It",
        "searchable": "deep smooth groove instrumental jazz",
        "mood": "Low-key, horn-laced smooth groove; mood poetry w/ subtle movement",
        "type": "ambient_search",
        "why_good": "Calming, sultry, slow-transition friendly"
    },
    {
        "id": 15,
        "track": "The Quiet Sounds - Motion Array",
        "searchable": "quiet sounds piano ambient instrumental",
        "mood": "Airy piano + soft pads; intimate spoken word beds",
        "type": "ambient_search",
        "why_good": "Ideal for minimalist, modern calm backgrounds"
    },
    {
        "id": 16,
        "track": "Grey Sky - Motion Array",
        "searchable": "grey sky lofi drift instrumental",
        "mood": "Smooth lo-fi drift; slow travel visuals, reflective verse",
        "type": "ambient_search",
        "why_good": "Ideal for slow, scenic reels"
    },
    {
        "id": 17,
        "track": "Under The Clouds - Motion Array",
        "searchable": "under clouds gentle piano beat instrumental",
        "mood": "Gentle piano + soft beat; morning pages, gentle love poems",
        "type": "ambient_search",
        "why_good": "Perfect for chill lifestyle & relaxed reels"
    },
    {
        "id": 18,
        "track": "Coffee Lofi - Pixabay",
        "searchable": "coffee lofi cafe instrumental",
        "mood": "Cozy café loop; journal poems, study vibes, ASMR text lines",
        "type": "ambient_search",
        "why_good": "Chill / Lofi / Coffee vibes for contemplative content"
    },
    {
        "id": 19,
        "track": "Coffee Mornings - Eli Harper",
        "searchable": "Eli Harper Coffee Mornings acoustic instrumental",
        "mood": "Warm acoustic fingerstyle; slow ritual / sunrise poetry",
        "type": "spotify_instrumental",
        "why_good": "Chill acoustic used in journaling & café reels"
    },
    {
        "id": 20,
        "track": "Sky Above - Yuna Taro",
        "searchable": "Yuna Taro Sky Above peaceful instrumental",
        "mood": "Peaceful wordless ambience; nature poems, breathwork captions",
        "type": "spotify_instrumental",
        "why_good": "Peaceful instrumental for yoga / calm scenes"
    }
]

def download_slow_track(track_info, index, total):
    """Download a single slow poetry track, prioritizing instrumental versions"""
    track_name = track_info["track"]
    search_query = track_info["searchable"]
    track_type = track_info["type"]
    
    print(f"🎵 [{index}/{total}] Downloading: {track_name}")
    print(f"    🎭 Mood: {track_info['mood']}")
    print(f"    💫 Why good: {track_info['why_good']}")
    
    try:
        # Always search for instrumental versions first
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
            print(f"⚠️  Primary search failed, trying alternative...")
            
            # Try without "instrumental" keyword for hard-to-find tracks
            alt_search = search_query.replace(" instrumental", "")
            cmd_alt = [
                "spotdl", 
                "download", 
                alt_search,
                "--output", str(audio_dir),
                "--format", "mp3",
                "--overwrite", "force"
            ]
            
            result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=120)
            
            if result_alt.returncode == 0:
                print(f"✅ Downloaded (alternative): {track_name}")
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
    """Trim all downloaded tracks to 30-second segments perfect for poetry Reels"""
    print("\n🎬 Processing tracks to 30-second poetry segments...")
    
    mp3_files = list(audio_dir.glob("*.mp3"))
    
    if not mp3_files:
        print("❌ No audio files found to process!")
        return 0
    
    processed_count = 0
    
    for i, file_path in enumerate(mp3_files, 1):
        print(f"✂️  [{i}/{len(mp3_files)}] Processing: {file_path.name}")
        
        # Create output filename for slow poetry tracks
        output_name = f"slow_poetry_{i:02d}_{file_path.stem[:30]}_30s.mp3"
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
            # For slow/relaxed tracks, we want the most melodic part
            if total_duration > 90:
                # Skip intro, get the main melodic section
                start_time = total_duration * 0.3  # Start after 30% 
            elif total_duration > 60:
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
            
            result = subprocess.run(trim_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created: {output_name}")
                processed_count += 1
                
                # Remove original long file
                try:
                    file_path.unlink()
                    print(f"🗑️  Removed original: {file_path.name}")
                except Exception as e:
                    print(f"⚠️  Could not remove original: {e}")
            else:
                print(f"❌ Failed to process: {file_path.name}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
    
    return processed_count

def convert_to_instrumental():
    """Convert all tracks to instrumental versions by removing vocals"""
    print("\n🎼 Converting to instrumental versions...")
    
    # Find all 30-second tracks
    track_files = list(audio_dir.glob("slow_poetry_*_30s.mp3"))
    
    if not track_files:
        print("❌ No tracks found to convert!")
        return 0
    
    converted_count = 0
    
    for i, track_path in enumerate(track_files, 1):
        print(f"🎼 [{i}/{len(track_files)}] Converting: {track_path.name}")
        
        # Create instrumental filename
        instrumental_name = track_path.name.replace("_30s.mp3", "_instrumental_30s.mp3")
        instrumental_path = audio_dir / instrumental_name
        
        try:
            # Method 1: Center channel extraction (removes most vocals)
            cmd = [
                "ffmpeg", 
                "-i", str(track_path),
                "-af", "pan=mono|c0=0.5*c0+-0.5*c1",  # Remove center channel (vocals)
                "-ac", "2",  # Convert back to stereo
                "-y",  # Overwrite output
                str(instrumental_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Converted: {instrumental_name}")
                converted_count += 1
                
                # Remove original vocal version
                try:
                    track_path.unlink()
                    print(f"🗑️  Removed vocal version: {track_path.name}")
                except Exception as e:
                    print(f"⚠️  Could not remove original: {e}")
            else:
                print(f"❌ Failed to convert: {track_path.name}")
                
        except Exception as e:
            print(f"❌ Error converting {track_path.name}: {e}")
    
    return converted_count

def main():
    print("🎭 Slow, Relaxed, Smooth Poetry Audio Downloader")
    print("=" * 60)
    print("🎯 Downloading contemplative, reflective tracks perfect for poetry")
    print("🎼 Automatically converts to instrumental versions")
    
    # Get user input
    try:
        print(f"\nAvailable tracks: {len(SLOW_POETRY_AUDIOS)}")
        max_tracks = input("How many slow poetry tracks to download? (1-20, default: 10): ").strip()
        max_tracks = int(max_tracks) if max_tracks else 10
        max_tracks = min(max_tracks, len(SLOW_POETRY_AUDIOS))
    except ValueError:
        max_tracks = 10
    
    print(f"\n🚀 Starting download of {max_tracks} slow poetry audios...")
    
    successful_downloads = 0
    tracks_to_download = SLOW_POETRY_AUDIOS[:max_tracks]
    
    # Download tracks
    for i, track_info in enumerate(tracks_to_download, 1):
        if download_slow_track(track_info, i, max_tracks):
            successful_downloads += 1
        
        # Small delay between downloads
        time.sleep(2)
        print()  # Add space between downloads
    
    print(f"\n📊 Download Summary:")
    print(f"✅ Successfully downloaded: {successful_downloads}/{max_tracks} tracks")
    
    if successful_downloads > 0:
        # Process to 30-second segments
        processed_count = trim_tracks_to_30_seconds()
        
        # Convert to instrumental versions
        converted_count = convert_to_instrumental()
        
        # Final summary
        print(f"\n🎉 Final Results:")
        print(f"📁 Location: {audio_dir.absolute()}")
        print(f"✅ Downloaded: {successful_downloads} tracks")
        print(f"✂️  Processed: {processed_count} to 30-second segments")
        print(f"🎼 Converted: {converted_count} to instrumental versions")
        print(f"⏱️  Duration: 30 seconds each (perfect for poetry Reels)")
        print(f"🎭 Style: Slow, relaxed, contemplative")
        
        # List final files
        final_files = list(audio_dir.glob("slow_poetry_*_instrumental_30s.mp3"))
        print(f"\n📜 Ready-to-use slow poetry instrumental tracks:")
        for i, file in enumerate(final_files[:15], 1):
            print(f"{i:2d}. {file.name}")
        
        if len(final_files) > 15:
            print(f"    ... and {len(final_files) - 15} more")
            
        print(f"\n🎬 These slow instrumental tracks are perfect for contemplative poetry!")
        
        # Show track info for first few
        print(f"\n💡 Track Usage Guide:")
        for track in tracks_to_download[:5]:  # Show first 5
            print(f"   • {track['track']}: {track['mood']}")
    else:
        print("\n❌ No tracks were successfully downloaded.")

if __name__ == "__main__":
    main() 