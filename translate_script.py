#!/usr/bin/env python3
"""
Translate Script - Convert existing podcast script to another language
Preserves audio tags and speaker format
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
config_path = Path(__file__).parent / 'config' / '.env'
load_dotenv(config_path)


def load_config():
    """Load podcast configuration"""
    config_path = Path('./config/podcast_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def translate_script(script, target_language, anthropic_key):
    """Translate script using Claude API"""
    
    language_names = {
        'de': 'German',
        'en': 'English',
        'nl': 'Dutch'
    }
    
    target_lang_name = language_names.get(target_language, target_language)
    
    prompt = f"""Translate the following podcast script to {target_lang_name}.

CRITICAL INSTRUCTIONS:
1. Keep ALL audio tags in [square brackets] exactly as they are - DO NOT translate them
2. Keep "Speaker A:" and "Speaker B:" labels in English
3. Translate ONLY the dialogue text
4. Preserve the conversational style and energy
5. Keep line breaks and formatting exactly the same
6. DO NOT add any commentary, just output the translated script
7. At the end, add "**SOURCES FOUND:**" followed by the original sources list

Original script:

{script}
"""
    
    print("\n[INFO] Calling Claude API for translation...")
    
    client = Anthropic(api_key=anthropic_key)
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        translated = response.content[0].text
        usage = response.usage
        
        print(f"[USAGE] Claude - Input: {usage.input_tokens} tokens, Output: {usage.output_tokens} tokens")
        
        return translated, usage
        
    except Exception as e:
        print(f"[ERROR] Translation failed: {str(e)}")
        return None, None


def generate_audio(script, config, language_code, speed, project_name):
    """Generate audio using existing generate_audio logic"""
    # Import from main pipeline
    sys.path.insert(0, str(Path(__file__).parent))
    from podcast_pipeline import generate_audio as gen_audio, save_audio
    
    return gen_audio(script, config, language_code, 'production', speed, project_name)


def main():
    """Main translation workflow"""
    print("=== Translate Script ===\n")
    
    # Load config
    config = load_config()
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY not found in config/.env")
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
    
    # Select target language
    print("\nAvailable languages:")
    print("  1. Deutsch (German) - DE")
    print("  2. English - EN")
    print("  3. Nederlands (Dutch) - NL")
    
    lang_choice = input("\nTarget language (1-3): ").strip()
    language_map = {'1': 'de', '2': 'en', '3': 'nl'}
    target_language = language_map.get(lang_choice)
    
    if not target_language:
        print("Invalid choice")
        return
    
    # Confirm
    print(f"\nTranslate '{script_path.name}' to {target_language.upper()}?")
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    # Translate
    translated_script, usage = translate_script(original_script, target_language, anthropic_key)
    if not translated_script:
        print("Translation failed")
        return
    
    # Save translated script
    timestamp = datetime.now().strftime('%Y-%m-%d')
    translated_filename = f"{project_name}_{target_language}_{timestamp}_translated.txt"
    translated_path = Path(f"./projects/{project_name}/scripts/{translated_filename}")
    
    with open(translated_path, 'w', encoding='utf-8') as f:
        f.write(translated_script)
    
    print(f"\n✓ Translated script saved: {translated_path}")
    print(f"  ({len(translated_script)} chars)")
    
    # Ask if user wants to generate audio
    print("\nGenerate audio for translated script?")
    audio_choice = input("(y/N): ").strip().lower()
    
    if audio_choice == 'y':
        # Get speed
        default_speed = config['languages'].get(target_language, {}).get('speed', 1.0)
        speed_input = input(f"\nSpeech speed (0.7-1.2, default {default_speed}, Enter to use default): ").strip()
        
        if speed_input:
            try:
                speed = float(speed_input)
                speed = max(0.7, min(1.2, speed))
            except ValueError:
                speed = default_speed
        else:
            speed = default_speed
        
        print(f"\n[INFO] Generating audio with speed {speed}...")
        
        # Import and use generate_audio from main pipeline
        sys.path.insert(0, str(Path(__file__).parent))
        from podcast_pipeline import generate_audio, save_audio, clean_script_for_audio
        
        # Clean script
        cleaned_script = clean_script_for_audio(translated_script)
        
        # Generate audio
        audio_data, chars = generate_audio(cleaned_script, config, target_language, 'production', speed, project_name)
        
        if audio_data:
            # Save audio
            audio_path = save_audio(audio_data, project_name, f"translated_{target_language}", target_language, 'production')
            print(f"\n✓ Audio saved: {audio_path}")
            print(f"  Characters: {chars}")
        else:
            print("\n✗ Audio generation failed")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
