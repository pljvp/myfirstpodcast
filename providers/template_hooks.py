"""
Provider Template Hooks
Loads provider-specific template content for script generation.
Handles placeholder substitution in templates.
"""

import yaml
from pathlib import Path


def load_provider_hooks(provider_name: str) -> dict:
    """
    Load template hooks for a specific provider.

    Args:
        provider_name: 'elevenlabs' or 'cartesia'

    Returns:
        dict with provider configuration

    Raises:
        ValueError: If provider config not found
    """
    config_path = Path(__file__).parent / 'configs' / f'{provider_name}.yaml'

    if not config_path.exists():
        raise ValueError(f"No config found for provider: {provider_name}. "
                        f"Expected: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_template_substitutions(provider_name: str, duration_minutes: int) -> dict:
    """
    Get all template placeholder substitutions for a provider.

    Calculates duration-aware values (interruption counts, variety counts, etc.)

    Args:
        provider_name: 'elevenlabs' or 'cartesia'
        duration_minutes: Podcast duration in minutes

    Returns:
        dict mapping placeholder names to values:
        - PROVIDER_EMOTION_TAGS: Emotion tag instructions
        - PROVIDER_EXAMPLES: Example dialogue
        - PROVIDER_CHECKLIST: Quality checklist
        - PROVIDER_NAME: Provider display name
        - PROVIDER_TAG: Provider tag (11LB, CRTS)
    """
    hooks = load_provider_hooks(provider_name)

    # Calculate duration-aware values
    checklist = hooks.get('checklist', '')

    if provider_name == 'elevenlabs':
        # Calculate interruption count: base + (duration / 5)
        base = hooks.get('interruption_base', 5)
        per_5min = hooks.get('interruption_per_5min', 1)
        interruption_min = base + (duration_minutes // 5) * per_5min
        interruption_max = interruption_min + 2
        checklist = checklist.replace(
            '{interruption_count}',
            f'{interruption_min}-{interruption_max}'
        )

    elif provider_name == 'cartesia':
        # Calculate variety count: base + (duration / 3)
        variety_base = hooks.get('variety_base', 10)
        variety_per_3min = hooks.get('variety_per_3min', 1)
        variety_count = variety_base + (duration_minutes // 3) * variety_per_3min
        checklist = checklist.replace('{variety_count}', str(variety_count))

        # Calculate exchange count: base + (duration / 5)
        exchange_base = hooks.get('exchange_base', 3)
        exchange_per_5min = hooks.get('exchange_per_5min', 1)
        exchange_count = exchange_base + (duration_minutes // 5) * exchange_per_5min
        checklist = checklist.replace('{exchange_count}', str(exchange_count))

    return {
        'PROVIDER_EMOTION_TAGS': hooks.get('emotion_tags', ''),
        'PROVIDER_EXAMPLES': hooks.get('examples', ''),
        'PROVIDER_CHECKLIST': checklist,
        'PROVIDER_NAME': hooks.get('provider_name', provider_name),
        'PROVIDER_TAG': hooks.get('provider_tag', ''),
    }


def substitute_template_placeholders(template_content: str, provider_name: str,
                                     duration_minutes: int) -> str:
    """
    Substitute all {PROVIDER_*} placeholders in template content.

    Args:
        template_content: Template text with placeholders
        provider_name: 'elevenlabs' or 'cartesia'
        duration_minutes: Podcast duration in minutes

    Returns:
        Template with placeholders replaced by provider-specific content
    """
    substitutions = get_template_substitutions(provider_name, duration_minutes)

    result = template_content
    for key, value in substitutions.items():
        placeholder = '{' + key + '}'
        result = result.replace(placeholder, value)

    return result


def get_supported_providers() -> list:
    """Return list of supported provider names."""
    configs_dir = Path(__file__).parent / 'configs'
    return [f.stem for f in configs_dir.glob('*.yaml')]
