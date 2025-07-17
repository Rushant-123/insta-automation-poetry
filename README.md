# Poetry Video Generator

An automated service for generating beautiful poetry videos with peaceful backgrounds and soothing music, designed for Instagram Reels.

## Features

- 🎨 **Multiple Themes**: Nature, Ocean, Sunset, Forest, Minimal themes with custom styling
- 📝 **Poetry Curation**: Public domain poetry collection with theme-based selection
- 🎬 **Professional Animations**: Fade-in, typewriter, slide-up, word-by-word effects
- 🎵 **Background Music**: Automatic audio integration with peaceful soundtracks
- 📱 **Instagram Ready**: 1080x1920 vertical format optimized for Reels
- ☁️ **S3 Integration**: Automatic upload and URL generation
- 🚀 **REST API**: Simple API for integration with existing automation systems

## Architecture

```
Poetry/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── config/
│   ├── settings.py        # Configuration management
│   └── themes.py          # Theme definitions
├── services/
│   ├── poetry_service.py  # Poetry curation
│   ├── video_service.py   # Video generation
│   └── s3_service.py      # Cloud storage
├── models/
│   └── schemas.py         # API models
├── utils/
│   ├── text_animator.py   # Text effects
│   └── video_composer.py  # Video composition
└── assets/
    ├── backgrounds/       # Background videos
    ├── audio/            # Music files
    └── fonts/            # Typography assets
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Poetry

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with your configuration:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-poetry-videos-bucket

# Application Configuration
DEBUG=false
```

### 3. Asset Setup (Optional)

Add your own assets for richer content:

```bash
# Add background videos
mkdir -p assets/backgrounds
# Copy your nature/peaceful videos (.mp4, .mov, .avi)

# Add background music
mkdir -p assets/audio
# Copy your soothing music files (.mp3, .wav, .m4a)

# Add custom fonts
mkdir -p assets/fonts
# Copy your font files (.ttf, .otf)
```

### 4. Run the Service

```bash
# Development mode
python main.py

# Production mode with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Generate Poetry Video

**POST** `/generate-video`

```json
{
  "theme": "nature",
  "text_style": "elegant",
  "animation": "fade_in",
  "custom_poetry": "Optional custom poetry text...",
  "duration": 18
}
```

**Response:**
```json
{
  "success": true,
  "video_url": "https://your-bucket.s3.amazonaws.com/poetry-videos/uuid.mp4",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "theme": "nature",
  "poetry_lines": ["Line 1", "Line 2", "Line 3", "Line 4"],
  "duration": 18
}
```

### Available Themes

**GET** `/themes`

Returns all available themes with their configurations.

### Random Poetry

**GET** `/poetry/random`

Get a random poetry for testing.

## Themes

### 🌿 Nature
- **Colors**: Earth greens and natural tones
- **Animation**: Gentle fade-in effects
- **Style**: Elegant serif typography

### 🌊 Ocean  
- **Colors**: Ocean blues and whites
- **Animation**: Slide-up transitions
- **Style**: Modern sans-serif

### 🌅 Sunset
- **Colors**: Warm golds and oranges
- **Animation**: Gentle zoom effects
- **Style**: Classic serif fonts

### 🌲 Forest
- **Colors**: Deep forest greens
- **Animation**: Word-by-word reveals
- **Style**: Elegant typography

### ⚪ Minimal
- **Colors**: Clean grays and whites
- **Animation**: Typewriter effects
- **Style**: Modern minimal fonts

## Configuration

### Video Settings

```python
# Default settings in config/settings.py
VIDEO_WIDTH = 1080      # Instagram Reels width
VIDEO_HEIGHT = 1920     # Instagram Reels height  
VIDEO_DURATION = 18     # Seconds
VIDEO_FPS = 24          # Frames per second
```

### Poetry Settings

```python
MIN_LINES = 4           # Minimum poetry lines
MAX_LINES = 8           # Maximum poetry lines
```

### Audio Settings

```python
AUDIO_FADE_DURATION = 1.0  # Seconds for fade in/out
```

## Integration Examples

### Cron Job Integration

```python
import requests

# Generate daily poetry video
response = requests.post("http://your-server:8000/generate-video", json={
    "theme": "nature",
    "duration": 20
})

video_data = response.json()
if video_data["success"]:
    video_url = video_data["video_url"]
    # Pass to your Instagram upload service
```

### Webhook Integration

```python
# Flask webhook example
@app.route('/generate-poetry-webhook', methods=['POST'])
def generate_poetry():
    theme = request.json.get('theme', 'nature')
    
    # Call poetry service
    response = requests.post("http://poetry-service:8000/generate-video", json={
        "theme": theme
    })
    
    return response.json()
```

## Development

### Adding New Themes

1. Add theme configuration in `config/themes.py`:

```python
ThemeType.CUSTOM = "custom"

THEME_CONFIGS[ThemeType.CUSTOM] = {
    "name": "Custom Theme",
    "description": "Your custom theme description",
    "background_keywords": ["custom", "keywords"],
    "color_palette": {
        "primary": "#your_color",
        "secondary": "#your_color",
        "accent": "#your_color",
        "background_overlay": "rgba(0, 0, 0, 0.3)"
    },
    "text_style": TextStyle.MODERN,
    "animation": AnimationType.FADE_IN,
    "font_family": "sans-serif",
    "font_size": 48,
    "line_spacing": 1.4,
    "poetry_themes": ["theme", "keywords"]
}
```

### Adding New Poetry

Poetry is automatically managed through the `PoetryService`. To add custom poetry:

```python
from services.poetry_service import PoetryService

poetry_service = PoetryService()
await poetry_service.add_custom_poetry(
    lines=["Your custom", "poetry lines", "go here"],
    author="Author Name",
    title="Poem Title"
)
```

### Custom Background Videos

Place video files in `assets/backgrounds/` directory:
- Supported formats: `.mp4`, `.mov`, `.avi`
- Recommended: 15-30 seconds minimum duration
- Resolution: Any (will be automatically resized)

### Custom Audio

Place audio files in `assets/audio/` directory:
- Supported formats: `.mp3`, `.wav`, `.m4a`
- Recommended: Peaceful, instrumental music
- Volume: Will be automatically adjusted to 30%

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Required:
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket for video storage

Optional:
- `AWS_REGION`: AWS region (default: us-east-1)
- `DEBUG`: Debug mode (default: false)
- `VIDEO_DURATION`: Default duration (default: 18)

## Troubleshooting

### Common Issues

1. **MoviePy Installation**: May require system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg imageio
   
   # macOS
   brew install ffmpeg
   ```

2. **S3 Permissions**: Ensure your AWS credentials have:
   - `s3:PutObject`
   - `s3:PutObjectAcl`
   - `s3:GetObject`

3. **Memory Usage**: Video generation is memory-intensive. Recommended:
   - 4GB+ RAM for production
   - SSD storage for temporary files

### Performance Tips

- Use SSD storage for temporary files
- Implement video caching for popular themes
- Consider video pre-generation for faster response times
- Monitor memory usage during video generation

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For questions or issues:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub 