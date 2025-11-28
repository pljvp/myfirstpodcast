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


def extract_language_from_filename(filename):
    """Extract language code from filename like 'project_DE_2025-11-28_draft1.txt'"""
    parts = filename.split('_')
    # Look for 2-letter uppercase code
    for part in parts:
        if len(part) == 2 and part.isupper() and part in ['DE', 'EN', 'NL']:
            return part.lower()
    return 'en'  # Default to English if not found


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


def main():
    """Main translation workflow"""
    print("=== Translate Script ===\n")
    
    # Load config
    config = load_config()
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
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
    
    # Extract source language from filename
    source_lang = extract_language_from_filename(script_path.name)
    
    print(f"\nLoaded: {script_path.name}")
    print(f"Detected source language: {source_lang.upper()}")
    print(f"Script length: {len(original_script)} chars")
    
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
    print(f"\nTranslate '{script_path.name}'")
    print(f"  From: {source_lang.upper()} → To: {target_language.upper()}")
    confirm = input("\nContinue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    # Translate
    translated_script, usage = translate_script(original_script, target_language, anthropic_key)
    if not translated_script:
        print("Translation failed")
        return
    
    # Save translated script with proper naming
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    lang_upper = target_language.upper()
    translated_filename = f"{project_name}_{lang_upper}_{timestamp}_draft1.txt"
    translated_path = Path(f"./projects/{project_name}/scripts/{translated_filename}")
    
    with open(translated_path, 'w', encoding='utf-8') as f:
        f.write(translated_script)
    
    print(f"\n✓ Translated script saved: {translated_path}")
    print(f"  ({len(translated_script)} chars)")
    
    # Ask if user wants to generate audio
    if not elevenlabs_key:
        print("\n[INFO] ELEVENLABS_API_KEY not found - skipping audio generation option")
        print("Done!")
        return
    
    print("\nGenerate audio for translated script?")
    audio_choice = input("(y/N): ").strip().lower()
    
    if audio_choice == 'y':
        # Select mode
        print("\nSelect audio mode:")
        print("  1. Prototype (lower quality, faster, testing)")
        print("  2. Production (high quality, final)")
        
        mode_input = input("\nMode (1-2, default=1): ").strip() or "1"
        mode = 'prototype' if mode_input == '1' else 'production'
        
        # Get speed
        # FIXED: Proper language mapping including Dutch
        language_key_map = {
            'de': 'german',
            'en': 'english',
            'nl': 'dutch'
        }
        language_key = language_key_map.get(target_language, 'english')
        
        default_speed = config['languages'].get(language_key, {}).get('speed', 1.0)
        speed_input = input(f"\nSpeech speed (0.7-1.2, default {default_speed}, Enter to use default): ").strip()
        
        if speed_input:
            try:
                speed = float(speed_input)
                speed = max(0.7, min(1.2, speed))
            except ValueError:
                speed = default_speed
        else:
            speed = default_speed
        
        print(f"\n[INFO] Generating audio with speed {speed} in {mode.upper()} mode...")
        
        # Import and use generate_audio from main pipeline
        sys.path.insert(0, str(Path(__file__).parent))
        from podcast_pipeline import generate_audio, save_audio, clean_script_for_audio
        
        # Clean script
        cleaned_script = clean_script_for_audio(translated_script)
        
        # Generate audio
        audio_data, chars = generate_audio(cleaned_script, config, target_language, mode, speed, project_name)
        
        if audio_data:
            # FIXED: Proper filename format with language code in capitals
            audio_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            audio_filename = f"{project_name}_{lang_upper}_{audio_timestamp}_{mode.upper()}.mp3"
            audio_path = Path(f"./projects/{project_name}/audio/{audio_filename}")
            
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"\n✓ Audio saved: {audio_path}")
            print(f"  Characters: {chars}")
            print(f"  Mode: {mode.upper()}")
            print(f"  Speed: {speed}")
        else:
            print("\n✗ Audio generation failed")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
