import numpy as np
from typing import List, Dict, Any, Tuple
from moviepy.editor import TextClip
from config.themes import AnimationType


class TextAnimator:
    """Utility class for creating advanced text animations."""
    
    def __init__(self):
        """Initialize text animator."""
        pass
        
    def create_typewriter_effect(
        self,
        text: str,
        fontsize: int,
        color: str,
        duration: float,
        font: str = None
    ) -> TextClip:
        """
        Create a typewriter effect for text.
        
        Args:
            text: Text to animate
            fontsize: Font size
            color: Text color
            duration: Animation duration
            font: Font path/name
            
        Returns:
            Animated text clip
        """
        # For now, simplified typewriter effect
        # In a full implementation, this would create character-by-character reveal
        clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font=font,
            method='caption'
        )
        
        # Apply gradual fade in to simulate typewriter
        clip = clip.set_duration(duration).fadein(duration * 0.8)
        return clip
        
    def create_word_by_word_effect(
        self,
        text: str,
        fontsize: int,
        color: str,
        duration: float,
        font: str = None
    ) -> List[TextClip]:
        """
        Create word-by-word reveal effect.
        
        Args:
            text: Text to animate
            fontsize: Font size
            color: Text color
            duration: Total animation duration
            font: Font path/name
            
        Returns:
            List of text clips for each word
        """
        words = text.split()
        word_clips = []
        
        word_duration = duration / len(words) if words else duration
        
        for i, word in enumerate(words):
            start_time = i * (word_duration * 0.5)  # Overlap words slightly
            
            clip = TextClip(
                word,
                fontsize=fontsize,
                color=color,
                font=font,
                method='caption'
            )
            
            clip = clip.set_start(start_time).set_duration(duration - start_time)
            clip = clip.fadein(0.3)
            
            word_clips.append(clip)
            
        return word_clips
        
    def create_gentle_zoom_effect(
        self,
        text: str,
        fontsize: int,
        color: str,
        duration: float,
        font: str = None
    ) -> TextClip:
        """
        Create gentle zoom and fade effect.
        
        Args:
            text: Text to animate
            fontsize: Font size
            color: Text color
            duration: Animation duration
            font: Font path/name
            
        Returns:
            Animated text clip
        """
        clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font=font,
            method='caption'
        )
        
        # Apply zoom effect (simplified - would need custom function for real zoom)
        clip = clip.set_duration(duration)
        clip = clip.fadein(duration * 0.3).fadeout(duration * 0.1)
        
        return clip
        
    def create_slide_up_effect(
        self,
        text: str,
        fontsize: int,
        color: str,
        duration: float,
        font: str = None,
        screen_height: int = 1920
    ) -> TextClip:
        """
        Create slide up from bottom effect.
        
        Args:
            text: Text to animate
            fontsize: Font size
            color: Text color
            duration: Animation duration
            font: Font path/name
            screen_height: Screen height for positioning
            
        Returns:
            Animated text clip
        """
        clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font=font,
            method='caption'
        )
        
        # Simplified slide effect - in full implementation would use custom position function
        clip = clip.set_duration(duration).fadein(0.5)
        
        return clip
        
    def apply_text_shadow(
        self,
        clip: TextClip,
        shadow_color: str = "black",
        offset: Tuple[int, int] = (2, 2)
    ) -> TextClip:
        """
        Apply text shadow effect.
        
        Args:
            clip: Text clip to add shadow to
            shadow_color: Shadow color
            offset: Shadow offset (x, y)
            
        Returns:
            Text clip with shadow
        """
        # This would require more complex implementation with compositing
        # For now, return original clip
        return clip
        
    def apply_text_stroke(
        self,
        clip: TextClip,
        stroke_color: str = "black",
        stroke_width: int = 2
    ) -> TextClip:
        """
        Apply text stroke/outline effect.
        
        Args:
            clip: Text clip to add stroke to
            stroke_color: Stroke color
            stroke_width: Stroke width
            
        Returns:
            Text clip with stroke
        """
        # This would require more complex implementation
        # For now, return original clip
        return clip 