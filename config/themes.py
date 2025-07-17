from typing import Dict, List, Any
from enum import Enum


class ThemeType(str, Enum):
    NATURE = "nature"
    MINIMAL = "minimal"
    OCEAN = "ocean"
    FOREST = "forest"
    SUNSET = "sunset"
    ABSTRACT = "abstract"


class TextStyle(str, Enum):
    ELEGANT = "elegant"
    MODERN = "modern"
    CLASSIC = "classic"
    HANDWRITTEN = "handwritten"


class AnimationType(str, Enum):
    FADE_IN = "fade_in"
    TYPEWRITER = "typewriter"
    SLIDE_UP = "slide_up"
    WORD_BY_WORD = "word_by_word"
    GENTLE_ZOOM = "gentle_zoom"


THEME_CONFIGS = {
    ThemeType.NATURE: {
        "name": "Nature",
        "description": "Peaceful nature scenes with organic themes",
        "background_keywords": ["forest", "trees", "grass", "leaves", "nature", "green"],
        "color_palette": {
            "primary": "#2d5016",
            "secondary": "#ffffff",
            "accent": "#8fbc8f",
            "background_overlay": "rgba(0, 0, 0, 0.3)"
        },
        "text_style": TextStyle.ELEGANT,
        "animation": AnimationType.FADE_IN,
        "font_family": "serif",
        "font_size": 48,
        "line_spacing": 1.4,
        "poetry_themes": ["nature", "growth", "seasons", "trees", "earth"]
    },
    
    ThemeType.OCEAN: {
        "name": "Ocean",
        "description": "Calming ocean and water scenes",
        "background_keywords": ["ocean", "waves", "water", "beach", "sea", "blue"],
        "color_palette": {
            "primary": "#1e3a8a",
            "secondary": "#ffffff",
            "accent": "#60a5fa",
            "background_overlay": "rgba(0, 0, 0, 0.25)"
        },
        "text_style": TextStyle.MODERN,
        "animation": AnimationType.SLIDE_UP,
        "font_family": "sans-serif",
        "font_size": 46,
        "line_spacing": 1.3,
        "poetry_themes": ["ocean", "water", "flow", "peace", "depth"]
    },
    
    ThemeType.SUNSET: {
        "name": "Sunset",
        "description": "Golden hour and sunset scenes",
        "background_keywords": ["sunset", "golden hour", "sky", "warm light", "horizon"],
        "color_palette": {
            "primary": "#92400e",
            "secondary": "#fef3c7",
            "accent": "#f59e0b",
            "background_overlay": "rgba(0, 0, 0, 0.2)"
        },
        "text_style": TextStyle.CLASSIC,
        "animation": AnimationType.GENTLE_ZOOM,
        "font_family": "serif",
        "font_size": 50,
        "line_spacing": 1.5,
        "poetry_themes": ["light", "time", "beauty", "reflection", "golden"]
    },
    
    ThemeType.MINIMAL: {
        "name": "Minimal",
        "description": "Clean, minimal aesthetic",
        "background_keywords": ["minimal", "clean", "simple", "geometric", "abstract"],
        "color_palette": {
            "primary": "#1f2937",
            "secondary": "#ffffff",
            "accent": "#6b7280",
            "background_overlay": "rgba(255, 255, 255, 0.1)"
        },
        "text_style": TextStyle.MODERN,
        "animation": AnimationType.TYPEWRITER,
        "font_family": "sans-serif",
        "font_size": 44,
        "line_spacing": 1.6,
        "poetry_themes": ["simplicity", "clarity", "essence", "truth", "moment"]
    },
    
    ThemeType.FOREST: {
        "name": "Forest",
        "description": "Deep forest and woodland scenes",
        "background_keywords": ["forest", "woods", "trees", "shadows", "green", "natural"],
        "color_palette": {
            "primary": "#14532d",
            "secondary": "#ecfdf5",
            "accent": "#22c55e",
            "background_overlay": "rgba(0, 0, 0, 0.4)"
        },
        "text_style": TextStyle.ELEGANT,
        "animation": AnimationType.WORD_BY_WORD,
        "font_family": "serif",
        "font_size": 47,
        "line_spacing": 1.4,
        "poetry_themes": ["forest", "mystery", "growth", "ancient", "wisdom"]
    }
}


def get_theme_config(theme: ThemeType) -> Dict[str, Any]:
    """Get configuration for a specific theme."""
    return THEME_CONFIGS.get(theme, THEME_CONFIGS[ThemeType.NATURE])


def get_available_themes() -> List[str]:
    """Get list of available theme names."""
    return [theme.value for theme in ThemeType] 