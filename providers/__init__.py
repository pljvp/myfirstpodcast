"""
TTS Provider modules for podcast generation

Available providers:
- ElevenLabsProvider: Full emotion dynamics with interruption tags
- CartesiaProvider: Optimized emotion controls with faster generation

Template hooks:
- get_template_substitutions(): Get provider-specific placeholder values
- substitute_template_placeholders(): Replace placeholders in templates
"""

from .elevenlabs import ElevenLabsProvider
from .cartesia import CartesiaProvider
from .template_hooks import (
    get_template_substitutions,
    substitute_template_placeholders,
    get_supported_providers,
    load_provider_hooks
)

__all__ = [
    'ElevenLabsProvider',
    'CartesiaProvider',
    'get_template_substitutions',
    'substitute_template_placeholders',
    'get_supported_providers',
    'load_provider_hooks'
]
