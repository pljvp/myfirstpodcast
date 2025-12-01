#!/usr/bin/env python3
"""
Tune Audio - Regenerate audio with DIFFERENT speaker speeds
Processes each segment individually to support per-voice speed control
"""

import os
import sys
import json
import re
import time
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


def detect_provider_from_filename(filename):
    """Detect TTS provider from script filename"""
    if '_CRTS_' in filename:
        return 'cartesia', 'CRTS'
    elif '_11LB_' in filename:
        return 'elevenlabs', '11LB'
    else:
        return None, None


def detect_language(script):
    """Detect script language from common words"""
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


def parse_script_to_segments(script):
    """Parse script into segments with speaker identification"""
    lines = script.split('\n')
    segments = []
    current_speaker = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        is_speaker_a = any(marker in line.lower() for marker in 
                          ['speaker a:', '**speaker a', 'speaker a -'])
        is_speaker_b = any(marker in line.lower() for marker in 
                          ['speaker b:', '**speaker b', 'speaker b -'])
        
        if is_speaker_a or is_speaker_b:
            # Save previous segment
            if current_text and current_speaker:
                text = ' '.join(current_text).strip()
                if text:
                    segments.append({
                        'speaker': current_speaker,
                        'text': text
                    })
            
            # Start new segment
            current_speaker = 'a' if is_speaker_a else 'b'
            text = line.split(':', 1)[-1].strip().replace('**', '').strip()
            current_text = [text] if text else []
        elif current_speaker:
            if not line.startswith('#') and not line.startswith('---'):
                current_text.append(line)
    
    # Final segment
    if current_text and current_speaker:
        text = ' '.join(current_text).strip()
        if text:
            segments.append({
                'speaker': current_speaker,
                'text': text
            })
    
    return segments


def generate_audio_cartesia_perspeaker(script, config, language_code, speed_a, speed_b, project_name):
    """Generate Cartesia audio with DIFFERENT speeds per speaker"""
    
    import requests
    
    api_key = os.getenv('CARTESIA_API_KEY')
    if not api_key:
        print("[ERROR] CARTESIA_API_KEY not found")
        return None, 0
    
    # Get voice IDs
    language = 'german' if language_code == 'de' else 'dutch' if language_code == 'nl' else 'english'
    voices = config['providers']['cartesia']['voices'][language]
    voice_ids = {
        'a': voices['speaker_a_female'],
        'b': voices['speaker_b_male']
    }
    
    # Convert speeds to Cartesia range
    cartesia_speed_a = (speed_a - 1.0) * 2.0
    cartesia_speed_b = (speed_b - 1.0) * 2.0
    cartesia_speed_a = max(-1.0, min(1.0, cartesia_speed_a))
    cartesia_speed_b = max(-1.0, min(1.0, cartesia_speed_b))
    
    print(f"\n[INFO] Provider: CARTESIA")
    print(f"[INFO] Per-speaker speeds:")
    print(f"  Speaker A: {speed_a} (ElevenLabs) → {cartesia_speed_a:.2f} (Cartesia)")
    print(f"  Speaker B: {speed_b} (ElevenLabs) → {cartesia_speed_b:.2f} (Cartesia)")
    
    # Parse script
    segments = parse_script_to_segments(script)
    print(f"[INFO] Processing {len(segments)} segments individually...")
    
    audio_parts = []
    total_chars = 0
    
    url = "https://api.cartesia.ai/tts/bytes"
    headers = {
        "X-API-Key": api_key,
        "Cartesia-Version": "2024-06-10",
        "Content-Type": "application/json"
    }
    
    for i, seg in enumerate(segments, 1):
        speaker = seg['speaker']
        text = seg['text']
        
        # Extract emotion tags
        emotion_pattern = r'\[(.*?)\]'
        emotions_found = re.findall(emotion_pattern, text)
        clean_text = re.sub(emotion_pattern, '', text).strip()
        
        if not clean_text:
            continue
        
        # Map emotions to Cartesia format
        emotion_map = {
            'excited': 'positivity:high',
            'enthusiastic': 'positivity:high',
            'curious': 'curiosity:high',
            'skeptical': 'curiosity:low',
            'surprised': 'surprise:high',
            'laughs': 'positivity:high',
            'chuckles': 'positivity:low',
            'thoughtful': 'curiosity:low',
            'impressed': 'positivity:high',
            'amused': 'positivity:low',
            'confused': 'curiosity:high',
        }
        
        emotion = 'curiosity:low'  # Default
        for emo in emotions_found:
            emo_lower = emo.lower()
            if emo_lower in emotion_map:
                emotion = emotion_map[emo_lower]
                break
        
        # Select speed based on speaker
        speed = cartesia_speed_a if speaker == 'a' else cartesia_speed_b
        voice_id = voice_ids[speaker]
        
        # API request
        payload = {
            "model_id": "sonic-english",
            "transcript": clean_text,
            "voice": {
                "mode": "id",
                "id": voice_id,
                "__experimental_controls": {
                    "speed": speed,
                    "emotion": [emotion]
                }
            },
            "output_format": {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100
            }
        }
        
        # Show progress
        speaker_label = "A" if speaker == 'a' else "B"
        speed_label = speed_a if speaker == 'a' else speed_b
        print(f"[{i}/{len(segments)}] Speaker {speaker_label} ({len(clean_text):4} chars) speed={speed_label:.2f} [{emotion}]")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                audio_parts.append(response.content)
                total_chars += len(clean_text)
            else:
                print(f"  ✗ Failed: {response.status_code} - {response.text[:100]}")
                continue
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            continue
    
    # Concatenate audio
    if audio_parts:
        audio_data = b''.join(audio_parts)
        print(f"\n✓ Generated {len(audio_parts)}/{len(segments)} segments ({len(audio_data) / 1024 / 1024:.1f} MB)")
        print(f"[USAGE] Cartesia - {total_chars} characters")
        return audio_data, total_chars
    else:
        print("\n✗ No audio generated")
        return None, 0


def generate_audio_elevenlabs_perspeaker(script, config, language_code, speed_a, speed_b, project_name):
    """Generate ElevenLabs audio with DIFFERENT speeds per speaker"""
    
    import requests
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("[ERROR] ELEVENLABS_API_KEY not found")
        return None, 0
    
    # Get voice IDs
    language = 'german' if language_code == 'de' else 'dutch' if language_code == 'nl' else 'english'
    voices = config['providers']['elevenlabs']['voices'][language]
    voice_ids = {
        'a': voices['speaker_a_female'],
        'b': voices['speaker_b_male']
    }
    
    print(f"\n[INFO] Provider: ELEVENLABS")
    print(f"[INFO] Per-speaker speeds:")
    print(f"  Speaker A: {speed_a}")
    print(f"  Speaker B: {speed_b}")
    
    # Parse script
    segments = parse_script_to_segments(script)
    print(f"[INFO] Processing {len(segments)} segments individually...")
    
    audio_parts = []
    total_chars = 0
    
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    
    for i, seg in enumerate(segments, 1):
        speaker = seg['speaker']
        text = seg['text']
        
        if not text.strip():
            continue
        
        # Select speed and voice based on speaker
        speed = speed_a if speaker == 'a' else speed_b
        voice_id = voice_ids[speaker]
        
        # API request
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "speed": speed,
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        # Show progress
        speaker_label = "A" if speaker == 'a' else "B"
        print(f"[{i}/{len(segments)}] Speaker {speaker_label} ({len(text):4} chars) speed={speed:.2f}")
        
        try:
            response = requests.post(
                f"{url}/{voice_id}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                audio_parts.append(response.content)
                total_chars += len(text)
            else:
                print(f"  ✗ Failed: {response.status_code} - {response.text[:100]}")
                continue
            
            # Rate limiting
            time.sleep(0.2)
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            continue
    
    # Concatenate audio
    if audio_parts:
        audio_data = b''.join(audio_parts)
        print(f"\n✓ Generated {len(audio_parts)}/{len(segments)} segments ({len(audio_data) / 1024 / 1024:.1f} MB)")
        print(f"[USAGE] ElevenLabs - {total_chars} characters")
        return audio_data, total_chars
    else:
        print("\n✗ No audio generated")
        return None, 0


def main():
    """Main audio tuning workflow"""
    print("=" * 60)
    print("TUNE AUDIO - Per-Speaker Speed Control")
    print("=" * 60)
    
    # Load config
    config = load_config()
    
    # Select project
    projects = list_projects()
    if not projects:
        print("No projects found. Run podcast_pipeline.py first.")
        return
    
    print("\nAvailable projects:")
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
        provider_name, provider_tag = detect_provider_from_filename(script.name)
        provider_display = f"[{provider_tag}]" if provider_tag else ""
        print(f"  {i}. {script.name} {provider_display} ({mtime.strftime('%Y-%m-%d %H:%M')})")
    
    choice = input(f"\nSelect script (1-{len(scripts)}): ").strip()
    try:
        script_idx = int(choice) - 1
        script_path = scripts[script_idx]
    except (ValueError, IndexError):
        print("Invalid choice")
        return
    
    # Detect provider
    provider_name, provider_tag = detect_provider_from_filename(script_path.name)
    
    if not provider_name:
        print(f"\n[ERROR] Could not detect provider from filename: {script_path.name}")
        print("Expected '_CRTS_' or '_11LB_' in filename")
        return
    
    print(f"\nDetected provider: {provider_name.upper()} (from filename)")
    
    # Check API key
    api_key_env = f"{provider_name.upper()}_API_KEY"
    if not os.getenv(api_key_env):
        print(f"[ERROR] {api_key_env} not found in config/.env")
        return
    
    print(f"[INFO] Audio will be generated using {provider_name.upper()}")
    
    # Load script
    with open(script_path, 'r', encoding='utf-8') as f:
        original_script = f.read()
    
    print(f"\nLoaded: {script_path.name} ({len(original_script)} chars)")
    
    # Detect language
    detected_lang = detect_language(original_script)
    print(f"Detected language: {detected_lang.upper()}")
    
    # Get speeds
    default_speed = 1.05
    
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
    print(f"  Speaker A (Female): {speed_a}")
    print(f"  Speaker B (Male): {speed_b}")
    print(f"  Provider: {provider_name.upper()}")
    print(f"\n  Note: Segments will be processed individually")
    confirm = input("\nContinue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    # Clean script
    sys.path.insert(0, str(Path(__file__).parent))
    from podcast_pipeline import clean_script_for_audio
    
    cleaned_script = clean_script_for_audio(original_script)
    
    # Generate audio with per-speaker speeds
    if provider_name == 'cartesia':
        audio_data, chars = generate_audio_cartesia_perspeaker(
            cleaned_script, config, detected_lang, speed_a, speed_b, project_name
        )
    else:  # elevenlabs
        audio_data, chars = generate_audio_elevenlabs_perspeaker(
            cleaned_script, config, detected_lang, speed_a, speed_b, project_name
        )
    
    if audio_data:
        # Save audio
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{project_name}_A{speed_a}_B{speed_b}_{detected_lang}_{timestamp}_{provider_tag}_TUNED.mp3"
        audio_path = Path(f"./projects/{project_name}/audio/{filename}")
        
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"\n✓ Audio saved: {audio_path}")
        print(f"  Characters: {chars}")
        print(f"  Speeds: A={speed_a}, B={speed_b}")
        print(f"  Provider: {provider_tag}")
    else:
        print("\n✗ Audio generation failed")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
