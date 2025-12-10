#!/usr/bin/env python3
"""
Tune Audio - Adjust speaker speeds after script generation
Supports per-speaker speed control for both Cartesia and ElevenLabs
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('config/.env')

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from podcast_pipeline import load_config, get_provider_instance
import re


def list_projects():
    """List available projects"""
    projects_dir = Path('./projects')
    if not projects_dir.exists():
        return []
    
    return [d.name for d in projects_dir.iterdir() if d.is_dir() and d.name != '__pycache__']


def list_scripts(project_name):
    """List available scripts for a project"""
    scripts_dir = Path(f'./projects/{project_name}/scripts')
    if not scripts_dir.exists():
        return []
    
    scripts = list(scripts_dir.glob('*.txt'))
    # Filter out source files
    scripts = [s for s in scripts if '_sources' not in s.name]
    return sorted(scripts, key=lambda x: x.stat().st_mtime, reverse=True)


def detect_provider_from_filename(filename):
    """Detect provider from filename tag"""
    if '_CRTS_' in filename:
        return 'cartesia'
    elif '_11LB_' in filename:
        return 'elevenlabs'
    else:
        print(f"WARNING: Could not detect provider from filename: {filename}")
        print("Defaulting to ElevenLabs")
        return 'elevenlabs'


def get_language_from_filename(filename):
    """Extract language code from filename"""
    # Format: project_LANG_date_time_provider_draft.txt
    match = re.search(r'_([A-Z]{2})_\d{4}-\d{2}-\d{2}', filename)
    if match:
        lang_code = match.group(1)
        return lang_code.lower()
    return 'de'  # default


def main():
    """Main audio tuning workflow"""
    print("=== Tune Audio - Per-Speaker Speed Control ===\n")
    
    # Load config
    try:
        config = load_config()
    except Exception as e:
        print(f"ERROR: Could not load config: {e}")
        return
    
    # Select project
    projects = list_projects()
    if not projects:
        print("No projects found in ./projects/")
        return
    
    print("Available projects:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project}")
    
    try:
        project_idx = int(input("\nSelect project number: ")) - 1
        project_name = projects[project_idx]
    except (ValueError, IndexError):
        print("Invalid selection")
        return
    
    # Select script
    scripts = list_scripts(project_name)
    if not scripts:
        print(f"No scripts found for project: {project_name}")
        return
    
    print(f"\nAvailable scripts for {project_name}:")
    for i, script in enumerate(scripts, 1):
        print(f"  {i}. {script.name}")
    
    try:
        script_idx = int(input("\nSelect script number: ")) - 1
        script_path = scripts[script_idx]
    except (ValueError, IndexError):
        print("Invalid selection")
        return
    
    # Detect provider and language from filename
    provider_name = detect_provider_from_filename(script_path.name)
    language_code = get_language_from_filename(script_path.name)
    
    print(f"\n[INFO] Detected provider: {provider_name.upper()}")
    print(f"[INFO] Detected language: {language_code.upper()}")
    
    # Check API key availability
    api_key_env = config['providers'][provider_name]['api_key_env']
    if not os.getenv(api_key_env):
        print(f"ERROR: {api_key_env} not found in config/.env")
        return
    
    # Get default speed
    default_speed = 1.0
    
    # Read script
    with open(script_path, 'r', encoding='utf-8') as f:
        script = f.read()
    
    # Get custom speeds per speaker
    print(f"\n{'='*60}")
    print("Speed range: 0.7 (slow) to 1.2 (fast)")
    print("Default: 1.0 (normal)")
    print(f"{'='*60}")
    
    try:
        speed_a_input = input(f"\nSpeaker A speed (0.7-1.2, default {default_speed}): ")
        speed_a = float(speed_a_input) if speed_a_input.strip() else default_speed
        
        speed_b_input = input(f"Speaker B speed (0.7-1.2, default {default_speed}): ")
        speed_b = float(speed_b_input) if speed_b_input.strip() else default_speed
        
        if not (0.7 <= speed_a <= 1.2) or not (0.7 <= speed_b <= 1.2):
            print("ERROR: Speeds must be between 0.7 and 1.2")
            return
    except ValueError:
        print("ERROR: Invalid speed value")
        return
    
    # Get provider instance
    provider = get_provider_instance(provider_name, config)
    if not provider:
        print("ERROR: Could not get provider instance")
        return
    
    # Get language mapping
    language_map = {'de': 'german', 'en': 'english', 'nl': 'dutch'}
    language = language_map.get(language_code, 'english')
    provider.language = language
    
    # Get voice IDs from provider config
    provider_config = config['providers'][provider_name]
    voice_config = provider_config['voices'][language]
    
    # Extract voice IDs - handle both formats (string and dict)
    def extract_voice_id(voice_data):
        if isinstance(voice_data, dict):
            return voice_data['id']
        return voice_data
    
    voice_id_a = extract_voice_id(voice_config.get('speaker_a_female') or voice_config.get('speaker_a_male'))
    voice_id_b = extract_voice_id(voice_config.get('speaker_b_male') or voice_config.get('speaker_b_female'))
    
    voice_ids = {
        'speaker_a': voice_id_a,
        'speaker_b': voice_id_b
    }
    
    # Generate audio with per-speaker speeds
    # Pass speeds as a DICT - providers handle this internally
    speed_dict = {
        'speaker_a': speed_a,
        'speaker_b': speed_b
    }
    
    print(f"\n[INFO] Generating audio with per-speaker speeds...")
    
    audio_data, char_count = provider.generate_audio(
        script=script,
        voice_ids=voice_ids,
        mode='production',
        speed=speed_dict,  # ← Pass dict instead of float
        project_name=project_name,
        use_config_speeds=False  # TUNE_AUDIO MODE - exact speeds
    )
    
    if not audio_data:
        print("ERROR: Audio generation failed")
        return
    
    # Save audio with speeds in filename
    from datetime import datetime
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H-%M')
    provider_tag = 'CRTS' if provider_name == 'cartesia' else '11LB'
    
    filename = f"{project_name}_A{speed_a:.2f}_B{speed_b:.2f}_{language_code}_{date}_{time}_{provider_tag}_TUNED.mp3"
    output_path = Path(f'./projects/{project_name}/audio/{filename}')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(audio_data)
    
    print(f"\n{'='*60}")
    print("✓ AUDIO SAVED")
    print(f"{'='*60}")
    print(f"File: {output_path.name}")
    print(f"Location: {output_path}")
    print(f"Speaker A speed: {speed_a}")
    print(f"Speaker B speed: {speed_b}")
    print(f"Provider: {provider_name.upper()}")
    print(f"Characters processed: {char_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
