import os
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClip
)
from moviepy.video.fx import resize, fadein, fadeout, crop
from PIL import Image, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)


class VideoComposer:
    """Utility class for advanced video composition operations."""
    
    def __init__(self):
        """Initialize video composer."""
        pass
        
    def apply_blur_effect(
        self,
        video_clip: VideoFileClip,
        blur_radius: float = 2.0
    ) -> VideoFileClip:
        """
        Apply blur effect to video background.
        
        Args:
            video_clip: Video clip to blur
            blur_radius: Blur radius
            
        Returns:
            Blurred video clip
        """
        # This would require implementing a custom MoviePy effect
        # For now, return original clip
        return video_clip
        
    def create_gradient_overlay(
        self,
        width: int,
        height: int,
        colors: List[str],
        direction: str = "vertical",
        opacity: float = 0.3
    ) -> ColorClip:
        """
        Create a gradient overlay.
        
        Args:
            width: Width of the overlay
            height: Height of the overlay
            colors: List of colors for gradient
            direction: Gradient direction ("vertical", "horizontal", "radial")
            opacity: Overlay opacity
            
        Returns:
            Gradient overlay clip
        """
        # Simplified implementation - create a semi-transparent color overlay
        # In full implementation, would create actual gradient
        color = self._hex_to_rgb(colors[0]) if colors else (0, 0, 0)
        
        overlay = ColorClip(
            size=(width, height),
            color=color,
            duration=1  # Will be set by caller
        ).set_opacity(opacity)
        
        return overlay
        
    def add_vignette_effect(
        self,
        video_clip: VideoFileClip,
        strength: float = 0.3
    ) -> VideoFileClip:
        """
        Add vignette (dark edges) effect to video.
        
        Args:
            video_clip: Video clip to add vignette to
            strength: Vignette strength (0.0 to 1.0)
            
        Returns:
            Video clip with vignette effect
        """
        # This would require custom effect implementation
        # For now, return original clip
        return video_clip
        
    def create_ken_burns_effect(
        self,
        image_clip: ImageClip,
        duration: float,
        zoom_ratio: float = 1.2,
        direction: str = "zoom_in"
    ) -> ImageClip:
        """
        Create Ken Burns effect (slow zoom and pan) for images.
        
        Args:
            image_clip: Image clip to animate
            duration: Effect duration
            zoom_ratio: Zoom ratio
            direction: Effect direction ("zoom_in", "zoom_out", "pan_left", "pan_right")
            
        Returns:
            Animated image clip
        """
        # Simplified implementation
        clip = image_clip.set_duration(duration)
        
        if direction == "zoom_in":
            clip = clip.fadein(duration * 0.1)
        elif direction == "zoom_out":
            clip = clip.fadeout(duration * 0.1)
            
        return clip
        
    def apply_color_grading(
        self,
        video_clip: VideoFileClip,
        temperature: float = 0.0,
        tint: float = 0.0,
        saturation: float = 1.0,
        brightness: float = 1.0,
        contrast: float = 1.0
    ) -> VideoFileClip:
        """
        Apply color grading to video.
        
        Args:
            video_clip: Video clip to grade
            temperature: Color temperature adjustment
            tint: Tint adjustment
            saturation: Saturation multiplier
            brightness: Brightness multiplier
            contrast: Contrast multiplier
            
        Returns:
            Color graded video clip
        """
        # This would require implementing custom color effects
        # For now, return original clip
        return video_clip
        
    def create_parallax_layers(
        self,
        background_clip: VideoFileClip,
        foreground_elements: List[Dict[str, Any]],
        duration: float
    ) -> CompositeVideoClip:
        """
        Create parallax effect with multiple layers.
        
        Args:
            background_clip: Background video
            foreground_elements: List of foreground elements with positions
            duration: Total duration
            
        Returns:
            Composite video with parallax effect
        """
        # Simplified implementation
        clips = [background_clip.set_duration(duration)]
        
        for element in foreground_elements:
            if 'clip' in element:
                clip = element['clip'].set_duration(duration)
                if 'position' in element:
                    clip = clip.set_position(element['position'])
                clips.append(clip)
                
        return CompositeVideoClip(clips)
        
    def add_particle_effects(
        self,
        video_clip: VideoFileClip,
        particle_type: str = "snow",
        intensity: float = 0.5
    ) -> CompositeVideoClip:
        """
        Add particle effects (snow, rain, etc.) to video.
        
        Args:
            video_clip: Base video clip
            particle_type: Type of particles ("snow", "rain", "leaves")
            intensity: Effect intensity
            
        Returns:
            Video with particle effects
        """
        # This would require complex particle system implementation
        # For now, return original clip as composite
        return CompositeVideoClip([video_clip])
        
    def create_text_background(
        self,
        width: int,
        height: int,
        color: str,
        opacity: float = 0.7,
        blur_radius: float = 10
    ) -> ColorClip:
        """
        Create a background for text with blur and opacity.
        
        Args:
            width: Background width
            height: Background height
            color: Background color
            opacity: Background opacity
            blur_radius: Blur radius for soft edges
            
        Returns:
            Text background clip
        """
        bg_color = self._hex_to_rgb(color)
        
        background = ColorClip(
            size=(width, height),
            color=bg_color,
            duration=1  # Will be set by caller
        ).set_opacity(opacity)
        
        return background
        
    def apply_motion_blur(
        self,
        video_clip: VideoFileClip,
        blur_amount: float = 1.0
    ) -> VideoFileClip:
        """
        Apply motion blur effect to video.
        
        Args:
            video_clip: Video clip to blur
            blur_amount: Amount of motion blur
            
        Returns:
            Video clip with motion blur
        """
        # This would require custom implementation
        # For now, return original clip
        return video_clip
        
    def create_smooth_transitions(
        self,
        clips: List[VideoFileClip],
        transition_duration: float = 1.0,
        transition_type: str = "crossfade"
    ) -> VideoFileClip:
        """
        Create smooth transitions between video clips.
        
        Args:
            clips: List of video clips to transition between
            transition_duration: Duration of each transition
            transition_type: Type of transition ("crossfade", "slide", "fade")
            
        Returns:
            Video with smooth transitions
        """
        if not clips:
            return None
            
        if len(clips) == 1:
            return clips[0]
            
        # Simplified crossfade implementation
        result_clips = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                # First clip: fade in at start
                result_clips.append(clip.fadein(transition_duration))
            elif i == len(clips) - 1:
                # Last clip: fade out at end
                result_clips.append(clip.fadeout(transition_duration))
            else:
                # Middle clips: fade in and out
                result_clips.append(
                    clip.fadein(transition_duration).fadeout(transition_duration)
                )
                
        # Concatenate with overlaps for crossfade effect
        from moviepy.editor import concatenate_videoclips
        return concatenate_videoclips(result_clips, method="compose")
        
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def _create_noise_texture(
        self,
        width: int,
        height: int,
        intensity: float = 0.1
    ) -> np.ndarray:
        """Create noise texture for effects."""
        noise = np.random.random((height, width, 3)) * intensity
        return (noise * 255).astype(np.uint8) 