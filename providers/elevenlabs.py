"""
ElevenLabs TTS Provider
Optimized for full emotion dynamics with interruption support
"""

import re
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .base import TTSProvider


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs Text-to-Dialogue API implementation"""
    
    PROVIDER_TAG = "11LB"
    
    def __init__(self, api_key: str, config: dict, language='english'):
        super().__init__(api_key, config)
        self.api_url = "https://api.elevenlabs.io/v1/text-to-dialogue"
        self.language = language
    
    def _get_voice_config(self, speaker, language):
        """Get voice ID and default speed from config
        
        Supports both formats:
        - Old: "voice_id_string"
        - New: {"id": "voice_id", "default_speed": 0.97}
        
        Args:
            speaker: 'speaker_a' or 'speaker_b'
            language: Language code
            
        Returns:
            dict with 'id' and 'default_speed'
        """
        # Determine gender key
        gender = 'female' if speaker == 'speaker_a' else 'male'
        voice_key = f"{speaker}_{gender}"
        
        # Get config
        voice_config = self.config['voices'][language][voice_key]
        
        # Support both formats
        if isinstance(voice_config, dict):
            return {
                'id': voice_config['id'],
                'default_speed': voice_config.get('default_speed', 1.0)
            }
        else:
            # Backwards compatible (just voice ID string)
            return {
                'id': voice_config,
                'default_speed': 1.0
            }
    
    def get_voice_speeds(self, language):
        """Get default speeds for all voices (for display)
        
        Args:
            language: Language code
            
        Returns:
            dict with speaker keys and default speeds
        """
        speeds = {}
        for speaker in ['speaker_a', 'speaker_b']:
            config = self._get_voice_config(speaker, language)
            gender = 'female' if speaker == 'speaker_a' else 'male'
            speeds[f"{speaker}_{gender}"] = config['default_speed']
        return speeds
    
    def _extract_voice_id(self, voice_config):
        """Extract voice ID string from config (handles both old and new formats)
        
        Args:
            voice_config: Either a string (old format) or dict with 'id' key (new format)
            
        Returns:
            Voice ID string
        """
        if isinstance(voice_config, dict):
            return voice_config.get('id', voice_config)
        return voice_config
    
    def get_template_instructions(self) -> str:
        """Return ElevenLabs-optimized instructions"""
        return """
===================================
ELEVENLABS-OPTIMIZED TAGS
===================================

**USE FULL TAG SET FOR MAXIMUM DYNAMICS:**

Interruptions & Overlap (CRITICAL - Use 5-10 times):
[interrupting] - Speaker cuts into other's speech
[overlapping] - Brief simultaneous speech  
[interjecting] - Quick insertion

Pacing & Delivery:
[fast-paced] - Rapid excited delivery
[slowly] - Deliberate, thoughtful pace
[pause] - Brief hesitation
[quietly] - Softer volume
[loudly] - Increased volume

Complex Combinations (Stack multiple tags):
[nervous][hesitant] - Nervous AND hesitant delivery
[excited][fast-paced] - Very excited, rapid speech
[skeptical][slowly] - Doubtful, measured delivery

**EXAMPLE USAGE:**
Speaker A: [excited] [fast-paced] This is incredible!
Speaker B: [interrupting] [curious] Wait, what about—
Speaker A: [overlapping] [laughs] Exactly!

All standard emotion tags also supported:
[excited] [curious] [skeptical] [surprised] [thoughtful]
[confused] [amused] [impressed] [frustrated] [nervous]
[laughs] [chuckles] [sighs] [gasps] [hmm]
"""
    
    def parse_script_to_dialogue(self, script: str, voice_ids: Dict[str, str]) -> List[Dict]:
        """Parse script into ElevenLabs dialogue format"""
        lines = script.split('\n')
        dialogue = []
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
            
            if is_speaker_a:
                if current_text and current_speaker:
                    voice_config = voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b']
                    dialogue.append({
                        'voice_id': self._extract_voice_id(voice_config),
                        'text': ' '.join(current_text).strip()
                    })
                
                current_speaker = 'speaker_a'
                text = line.split(':', 1)[-1].strip().replace('**', '').strip()
                current_text = [text] if text else []
                
            elif is_speaker_b:
                if current_text and current_speaker:
                    voice_config = voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b']
                    dialogue.append({
                        'voice_id': self._extract_voice_id(voice_config),
                        'text': ' '.join(current_text).strip()
                    })
                
                current_speaker = 'speaker_b'
                text = line.split(':', 1)[-1].strip().replace('**', '').strip()
                current_text = [text] if text else []
                
            elif current_speaker:
                if not line.startswith('#') and not line.startswith('---'):
                    current_text.append(line)
        
        # FIXED: Correct syntax for final segment
        if current_text and current_speaker:
            voice_config = voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b']
            dialogue.append({
                'voice_id': self._extract_voice_id(voice_config),
                'text': ' '.join(current_text).strip()
            })
        
        return dialogue if dialogue else None
    
    def chunk_dialogue(self, inputs: List[Dict], max_chars: int = 4500) -> List[List[Dict]]:
        """Split dialogue into chunks"""
        chunks = []
        current_chunk = []
        current_length = 0
        
        for item in inputs:
            item_length = len(item['text'])
            
            if current_length + item_length > max_chars and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [item]
                current_length = item_length
            else:
                current_chunk.append(item)
                current_length += item_length
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def generate_audio(
        self, 
        script: str, 
        voice_ids: Dict[str, str],
        mode: str = 'prototype',
        speed: float = 1.0,
        project_name: Optional[str] = None,
        use_config_speeds: bool = True
    ) -> Tuple[Optional[bytes], int]:
        """Generate audio using ElevenLabs API
        
        Args:
            script: Formatted script
            voice_ids: Voice IDs for speakers
            mode: 'prototype' or 'production'
            speed: Base speed (float) or per-speaker dict {'speaker_a': 0.95, 'speaker_b': 1.05}
            project_name: Project name
            use_config_speeds: If True, multiply by per-voice defaults (pipeline mode)
                               If False, use speed directly (tune_audio mode)
        """
        # Check if speed is a dict (per-speaker) or float (single speed)
        speed_is_dict = isinstance(speed, dict)
        
        print(f"\n{'='*60}")
        print(f"TTS PROVIDER: ELEVENLABS")
        
        if speed_is_dict:
            print(f"Per-speaker speeds:")
            print(f"  Speaker A: {speed['speaker_a']}")
            print(f"  Speaker B: {speed['speaker_b']}")
        else:
            print(f"Base speed: {speed}")
            
            # Show per-voice speeds if enabled
            if use_config_speeds:
                print(f"Per-voice speed mode: ENABLED (pipeline)")
                voice_speeds = self.get_voice_speeds(self.language)
                for voice, default in voice_speeds.items():
                    final = speed * default
                    print(f"  {voice}: {default:.2f} → final: {final:.2f}")
            else:
                print(f"Per-voice speed mode: DISABLED (tune_audio - using exact speeds)")
        
        print(f"{'='*60}")
        
        dialogue = self.parse_script_to_dialogue(script, voice_ids)
        
        if not dialogue:
            print("\n[ERROR] Script format error - no Speaker A:/B: labels found")
            return None, 0
        
        # Add voice settings WITH per-voice speed support
        inputs = []
        for seg in dialogue:
            voice_id = seg['voice_id']
            
            # Find which speaker this is by comparing IDs
            speaker = None
            for spk in ['speaker_a', 'speaker_b']:
                spk_config = voice_ids.get(spk)
                spk_id = self._extract_voice_id(spk_config)
                if voice_id == spk_id:
                    speaker = spk
                    break
            
            if use_config_speeds:
                # PIPELINE MODE: Apply per-voice default
                if speaker:
                    voice_cfg = self._get_voice_config(speaker, self.language)
                    final_speed = speed * voice_cfg['default_speed']
                else:
                    final_speed = speed  # Fallback
            else:
                # TUNE_AUDIO MODE: Use speed directly
                if speed_is_dict:
                    # Per-speaker speeds provided
                    final_speed = speed.get(speaker, 1.0) if speaker else 1.0
                else:
                    # Single speed for all
                    final_speed = speed
            
            inputs.append({
                "text": seg['text'], 
                "voice_id": seg['voice_id'],
                "voice_settings": {"speed": final_speed}
            })
        
        total_length = sum(len(item['text']) for item in inputs)
        print(f"[DEBUG] Total dialogue: {total_length} characters, {len(dialogue)} segments")
        
        # Chunk if needed
        if total_length > 5000:
            print(f"[INFO] Splitting into chunks (>5000 chars)...")
            chunks = self.chunk_dialogue(inputs, max_chars=4500)
            print(f"[INFO] Created {len(chunks)} chunks")
        else:
            chunks = [inputs]
        
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        audio_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_length = sum(len(item['text']) for item in chunk)
            print(f"\n[Chunk {i}/{len(chunks)}] {len(chunk)} segments, {chunk_length} chars")
            
            # Save debug
            if project_name:
                self._save_debug_chunk(chunk, i, project_name)
            
            payload = {"inputs": chunk}
            
            # Retry logic
            for attempt in range(3):
                try:
                    if attempt > 0:
                        print(f"[RETRY] Attempt {attempt + 1}/3...")
                        time.sleep(2 * attempt)
                    
                    response = requests.post(
                        self.api_url, 
                        headers=headers, 
                        json=payload, 
                        stream=True, 
                        timeout=120
                    )
                    
                    if response.status_code != 200:
                        print(f"[ERROR] Status {response.status_code}: {response.text}")
                        if response.status_code == 500 and attempt < 2:
                            continue
                        response.raise_for_status()
                    
                    # Collect audio
                    chunk_audio = b''.join(response.iter_content(chunk_size=8192))
                    audio_parts.append(chunk_audio)
                    print(f"  ✓ Generated ({len(chunk_audio) / 1024 / 1024:.1f} MB)")
                    break
                    
                except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                    print(f"[ERROR] {type(e).__name__}: {str(e)}")
                    if attempt < 2:
                        continue
                    return None, 0
        
        # Concatenate
        audio_data = b''.join(audio_parts) if len(audio_parts) > 1 else audio_parts[0]
        
        print(f"\n✓ Complete ({len(audio_data) / 1024 / 1024:.1f} MB)")
        print(f"[USAGE] ElevenLabs - {total_length} characters")
        
        return audio_data, total_length
    
    def _save_debug_chunk(self, chunk: List[Dict], chunk_num: int, project_name: str):
        """Save chunk for debugging"""
        debug_path = Path(f"./projects/{project_name}/debug")
        debug_path.mkdir(parents=True, exist_ok=True)
        
        debug_file = debug_path / f"chunk_{chunk_num}_11LB.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
    
    def add_silence_padding(self, audio_bytes, intro_ms=1300, outro_ms=500):
        """Add silence before and after audio
        
        Args:
            audio_bytes: Audio data (MP3)
            intro_ms: Milliseconds of silence before
            outro_ms: Milliseconds of silence after
            
        Returns:
            Audio with silence padding
        """
        try:
            from pydub import AudioSegment
            import io
            
            # Load main audio
            main_audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            
            # Create silence
            intro_silence = AudioSegment.silent(duration=intro_ms)
            outro_silence = AudioSegment.silent(duration=outro_ms)
            
            # Combine
            final_audio = intro_silence + main_audio + outro_silence
            
            # Export
            output = io.BytesIO()
            final_audio.export(output, format="mp3", bitrate="192k")
            return output.getvalue()
            
        except Exception as e:
            print(f"[ERROR] Failed to add silence: {e}")
            return audio_bytes  # Return original if fails
