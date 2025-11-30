"""
TTS Provider modules for podcast generation

Available providers:
- ElevenLabsProvider: Full emotion dynamics with interruption tags
- CartesiaProvider: Optimized emotion controls with faster generation
"""

from .elevenlabs import ElevenLabsProvider
from .cartesia import CartesiaProvider

__all__ = ['ElevenLabsProvider', 'CartesiaProvider']
