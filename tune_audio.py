#!/usr/bin/env python3
"""
Tune Audio - Regenerate audio with different speaker speeds
Uses existing script, only changes ElevenLabs voice settings
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
config_path = Path(__file__).parent / 'config' / '.env'
load_dotenv(config_path)


def load_config():
    """Load podcast configuration"""
    config_path = Path('./config/podcast_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)




def extract_provider_from_filename(filename):
    """Extract provider tag from script filename"""
    if '_11LB_' in filename:
        return 'elevenlabs', '11LB'
    elif '_CRTS_' in filename:
        return 'cartesia', 'CRTS'
    else:
        # Default to ElevenLabs if no tag
        return 'elevenlabs', '11LB'

def list_projects():
    """List available projects"""
    projects_path = Path('./projects')
    if not projects_path.exists():
        return []
    return [p.name for p in projects_path.iterdir() if p.is_dir()]


def list_scripts(project_name):
    """List available scripts in project"""
    scripts_path = Path(f'./projects/{project_name}/scripts')
    if not scripts_path.exists():
        return []
    
    scripts = []
    for f in scripts_path.glob('*.txt'):
        if not f.name.endswith('_sources.txt'):
            scripts.append(f)
    return sorted(scripts, key=lambda x: x.stat().st_mtime, reverse=True)


def detect_language(script):
    """Detect script language from common words"""
    # Simple heuristic based on common words
    script_lower = script.lower()
    
    german_indicators = ['und', 'der', 'die', 'das', 'ist', 'aber', 'auch']
    dutch_indicators = ['van', 'het', 'een', 'de', 'dat', 'ook', 'niet']
    english_indicators = ['the', 'and', 'that', 'this', 'with', 'have']
    
    de_count = sum(1 for word in german_indicators if f' {word} ' in script_lower)
    nl_count = sum(1 for word in dutch_indicators if f' {word} ' in script_lower)
    en_count = sum(1 for word in english_indicators if f' {word} ' in script_lower)
    
    if de_count > max(nl_count, en_count):
        return 'de'
    elif nl_count > max(de_count, en_count):
        return 'nl'
    else:
        return 'en'


def generate_audio_with_custom_speeds(script, config, language_code, speed_a, speed_b, project_name, provider_name='elevenlabs'):
    """Generate audio with different speeds for Speaker A and B"""
    
    # Import provider modules
    sys.path.insert(0, str(Path(__file__).parent))
    from providers import ElevenLabsProvider, CartesiaProvider
    
    # Get provider instance
    if provider_name not in config.get('providers', {}):
        print(f"ERROR: Provider '{provider_name}' not in config")
        return None, 0
    
    provider_config = config['providers'][provider_name]
    api_key_env = provider_config.get('api_key_env')
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        print(f"ERROR: {api_key_env} not found in config/.env")
        return None, 0
    
    # Get language mapping and voice IDs
    language_map = {'de': 'german', 'en': 'english', 'nl': 'dutch'}
    language = language_map.get(language_code, 'english')
    
    if language not in provider_config.get('voices', {}):
        print(f"ERROR: No voices for {language} in provider {provider_name}")
        return None, 0
    
    voice_config = provider_config['voices'][language]
    voice_ids = {
        'speaker_a': voice_config.get('speaker_a_female') or voice_config.get('speaker_a_male'),
        'speaker_b': voice_config.get('speaker_b_male') or voice_config.get('speaker_b_female')
    }
    
    print(f"[INFO] Using custom speeds: Speaker A = {speed_a}, Speaker B = {speed_b}")
    print(f"[INFO] Provider: {provider_name.upper()}")
    
    # Create provider instance
    if provider_name == 'elevenlabs':
        provider = ElevenLabsProvider(api_key, provider_config)
    elif provider_name == 'cartesia':
        provider = CartesiaProvider(api_key, provider_config)
    else:
        print(f"ERROR: Unknown provider {provider_name}")
        return None, 0
    
    # Parse script using provider
    dialogue = provider.parse_script_to_dialogue(script, voice_ids)
    
    if not dialogue:
        print("ERROR: Could not parse script")
        return None, 0
    
    print(f"\n[INFO] Generating audio with custom speeds...")
    print(f"  Dialogue segments: {len(dialogue)}")
    
    # Generate with per-speaker speeds
    # Note: For now, we use average speed since providers don't directly support per-speaker
    # TODO: Implement per-speaker speed in provider classes
    avg_speed = (speed_a + speed_b) / 2
    print(f"[INFO] Using average speed {avg_speed:.2f} (per-speaker not yet supported)")
    
    audio_data, total_chars = provider.generate_audio(
        script, voice_ids, mode='production', speed=avg_speed, project_name=project_name
    )
    
    if audio_data:
        print(f"✓ Audio generated ({len(audio_data) / 1024 / 1024:.1f} MB)")
        print(f"[USAGE] {provider_name.upper()} - {total_chars} characters processed")
    
    return audio_data, total_chars


def main():
    """Main audio tuning workflow"""
    print("=== Tune Audio ===\n")
    
    # Load config
    config = load_config()
    
    if not os.getenv('ELEVENLABS_API_KEY'):
        print("ERROR: ELEVENLABS_API_KEY not found in config/.env")
        return
    
    # Select project
    projects = list_projects()
    if not projects:
        print("No projects found. Run podcast_pipeline.py first.")
        return
    
    print("Available projects:")
    for i, proj in enumerate(projects, 1):
        print(f"  {i}. {proj}")
    
    choice = input(f"\nSelect project (1-{len(projects)}): ").strip()
    try:
        project_idx = int(choice) - 1
        project_name = projects[project_idx]
    except (ValueError, IndexError):
        print("Invalid choice")
        return
    
    # Select script
    scripts = list_scripts(project_name)
    if not scripts:
        print(f"No scripts found in project '{project_name}'")
        return
    
    print(f"\nAvailable scripts in '{project_name}':")
    for i, script in enumerate(scripts, 1):
        mtime = datetime.fromtimestamp(script.stat().st_mtime)
        print(f"  {i}. {script.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
    
    choice = input(f"\nSelect script (1-{len(scripts)}): ").strip()
    try:
        script_idx = int(choice) - 1
        script_path = scripts[script_idx]
    except (ValueError, IndexError):
        print("Invalid choice")
        return
    
    # Load script
    with open(script_path, 'r', encoding='utf-8') as f:
        original_script = f.read()
    
    print(f"\nLoaded: {script_path.name} ({len(original_script)} chars)")
    
    # Detect language and provider
    detected_lang = detect_language(original_script)
    provider_name, provider_tag = extract_provider_from_filename(script_path.name)
    
    print(f"Detected language: {detected_lang.upper()}")
    print(f"Detected provider: {provider_name.upper()} (from filename)")
    print(f"[INFO] Audio will be generated using {provider_name.upper()}")
    
    # Get speeds - use proper language mapping
    language_map = {'de': 'german', 'en': 'english', 'nl': 'dutch'}
    language_key = language_map.get(detected_lang, 'english')
    default_speed = config['languages'].get(language_key, {}).get('speed', 1.0)
    
    print(f"\nCurrent default speed: {default_speed}")
    print("Speed range: 0.7 (slow) to 1.2 (fast)")
    print()
    
    speed_a_input = input(f"Speaker A speed (default {default_speed}): ").strip()
    if speed_a_input:
        try:
            speed_a = float(speed_a_input)
            speed_a = max(0.7, min(1.2, speed_a))
        except ValueError:
            speed_a = default_speed
    else:
        speed_a = default_speed
    
    speed_b_input = input(f"Speaker B speed (default {default_speed}): ").strip()
    if speed_b_input:
        try:
            speed_b = float(speed_b_input)
            speed_b = max(0.7, min(1.2, speed_b))
        except ValueError:
            speed_b = default_speed
    else:
        speed_b = default_speed
    
    # Confirm
    print(f"\nRegenerate audio with:")
    print(f"  Speaker A (Female Lead): {speed_a}")
    print(f"  Speaker B (Male Skeptic): {speed_b}")
    confirm = input("\nContinue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    # Clean script (remove sources)
    sys.path.insert(0, str(Path(__file__).parent))
    from podcast_pipeline import clean_script_for_audio, save_audio
    
    cleaned_script = clean_script_for_audio(original_script)
    
    # Generate audio
    audio_data, chars = generate_audio_with_custom_speeds(
        cleaned_script, 
        config, 
        detected_lang, 
        speed_a, 
        speed_b, 
        project_name
    )
    
    if audio_data:
        # Save audio with speeds in filename
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{project_name}_tuned_A{speed_a}_B{speed_b}_{detected_lang}_{timestamp}_TUNED.mp3"
        audio_path = Path(f"./projects/{project_name}/audio/{filename}")
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"\n✓ Audio saved: {audio_path}")
        print(f"  Characters: {chars}")
        print(f"  Speeds: A={speed_a}, B={speed_b}")
    else:
        print("\n✗ Audio generation failed")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
