# Poetry Video Generator - Setup Guide

## 🚀 Quick Start

Your Poetry video generator now supports **dynamic content fetching** from multiple sources! This guide will help you set up the enhanced features.

## 📋 Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ImageMagick** (required for text rendering):
   ```bash
   # macOS
   brew install imagemagick
   
   # Ubuntu/Debian
   sudo apt-get install imagemagick
   ```

## 🔑 API Keys Setup (Optional but Recommended)

### 1. Pexels API (Free Background Videos)
1. Go to [Pexels API](https://www.pexels.com/api/)
2. Create free account and get API key
3. Add to your environment:
   ```bash
   export PEXELS_API_KEY="your_pexels_api_key_here"
   ```

### 2. Pixabay API (Free Audio)
1. Go to [Pixabay API](https://pixabay.com/api/docs/)
2. Create free account and get API key
3. Add to your environment:
   ```bash
   export PIXABAY_API_KEY="your_pixabay_api_key_here"
   ```

### 3. AWS S3 (For Production)
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export S3_BUCKET_NAME="your-bucket-name"
```

## 🏃‍♂️ Running the Service

```bash
# Start the service
python main.py

# Service runs on http://localhost:8001
```

## 📊 Content Management

### Check Current Status
```bash
curl http://localhost:8001/content/status
```

### Fetch Background Videos (25 total, 5 per theme)
```bash
# Fetch nature backgrounds
curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=nature&count=5"

# Fetch ocean backgrounds  
curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=ocean&count=5"

# Fetch sunset backgrounds
curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=sunset&count=5"

# Fetch forest backgrounds
curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=forest&count=5"

# Fetch minimal backgrounds
curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=minimal&count=5"
```

### Fetch Poetry from Multiple Sources
```bash
# Fetch from Reddit poetry communities
curl -X POST "http://localhost:8001/content/fetch-poetry?source=reddit&count=20"

# Fetch from Poetry Foundation
curl -X POST "http://localhost:8001/content/fetch-poetry?source=poetry_foundation&count=15"

# Fetch from Poets.org
curl -X POST "http://localhost:8001/content/fetch-poetry?source=poets_org&count=15"

# Fetch from all sources
curl -X POST "http://localhost:8001/content/fetch-poetry?source=all&count=30"
```

### Fetch Background Audio
```bash
# Fetch peaceful music
curl -X POST "http://localhost:8001/content/fetch-audio?count=10"
```

## 🎬 Generate Enhanced Videos

After fetching content, your videos will automatically use:
- ✅ **Dynamic backgrounds** (theme-matched videos)
- ✅ **Curated poetry** (from Reddit, Poetry Foundation, Poets.org)
- ✅ **Peaceful music** (from Pixabay)

```bash
# Generate video with enhanced content
curl -X POST "http://localhost:8001/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "nature",
    "duration": 18
  }'
```

## 📂 Manual Content Addition

You can also manually add content to the directories:

### Background Videos
```bash
# Add your own videos
cp your_videos/* assets/backgrounds/
```

### Audio Files  
```bash
# Add your own music
cp your_music/* assets/audio/
```

### Supported Formats
- **Videos**: `.mp4`, `.mov`, `.avi`
- **Audio**: `.mp3`, `.wav`, `.m4a`
- **Duration**: Any length (auto-trimmed/looped to video duration)

## 🔧 Content Sources

### Poetry Sources
- **Reddit**: r/Poetry, r/OCPoetry, r/poems, r/poetry_critics
- **Poetry Foundation**: Classic and contemporary poems
- **Poets.org**: Academy of American Poets collection
- **Built-in**: 10 curated peaceful poems

### Background Video Sources  
- **Pexels**: Free HD videos (API-driven)
- **Manual**: Add your own videos to `assets/backgrounds/`

### Audio Sources
- **Pixabay**: Free music library (API-driven)
- **YouTube Audio Library**: Manual download recommended
- **Manual**: Add your own music to `assets/audio/`

## 🎯 Content Strategy

### Initial Setup (Recommended)
1. **Get API keys** for Pexels and Pixabay
2. **Fetch 25 background videos** (5 per theme)
3. **Fetch 50+ poems** from all sources  
4. **Fetch 10+ audio tracks**

### Ongoing Management
- **Weekly**: Fetch new poetry to keep content fresh
- **Monthly**: Add new background videos
- **As needed**: Add seasonal or themed content

## 🚀 Production Deployment

### Environment Variables
```bash
# Content APIs
PEXELS_API_KEY=your_pexels_key
PIXABAY_API_KEY=your_pixabay_key

# AWS S3 (for video storage)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your-bucket

# App Config
DEBUG=false
```

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# Initialize content
docker exec poetry-generator curl -X POST "http://localhost:8001/content/fetch-backgrounds?theme=nature&count=5"
```

## 📈 Scaling Tips

1. **Content Caching**: Content is cached locally, only fetch when needed
2. **API Rate Limits**: Built-in delays respect API limits
3. **Storage Management**: Monitor `assets/` directory size
4. **Content Rotation**: Regularly fetch new content for variety

## 🔍 Troubleshooting

### No Background Videos
- Check Pexels API key: `curl http://localhost:8001/content/status`
- Manually add videos to `assets/backgrounds/`

### No Audio
- Check Pixabay API key
- Manually add music to `assets/audio/`

### Poetry Scraping Issues
- Reddit API is rate-limited (automatic delays included)
- Poetry websites may block scraping (use built-in collection)

### Video Generation Fails
- Check ImageMagick installation: `which convert`
- Check disk space in `temp/` directory
- Review logs for specific errors

## 📚 API Documentation

Visit `http://localhost:8001/docs` for interactive API documentation with all endpoints and examples. 