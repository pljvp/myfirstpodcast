"""
Base TTS Provider - Abstract class for all TTS implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class TTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    PROVIDER_TAG = "BASE"  # Override in subclasses (e.g., "11LB", "CRTS")
    
    def __init__(self, api_key: str, config: dict):
        """
        Initialize TTS provider
        
        Args:
            api_key: API key for the TTS service
            config: Provider-specific configuration from podcast_config.json
        """
        self.api_key = api_key
        self.config = config
    
    @abstractmethod
    def generate_audio(
        self, 
        script: str, 
        voice_ids: Dict[str, str],
        mode: str = 'prototype',
        speed: float = 1.0,
        project_name: Optional[str] = None
    ) -> Tuple[Optional[bytes], int]:
        """
        Generate audio from script
        
        Args:
            script: Parsed dialogue script
            voice_ids: Dictionary mapping speaker_a/speaker_b to voice IDs
            mode: 'prototype' or 'production'
            speed: Speech speed multiplier (0.7-1.2)
            project_name: Project name for debug logging
        
        Returns:
            Tuple of (audio_data as bytes, character_count)
            Returns (None, 0) on failure
        """
        pass
    
    @abstractmethod
    def get_template_instructions(self) -> str:
        """
        Get provider-specific template instructions
        
        Returns:
            String with provider-optimized tag instructions
        """
        pass
