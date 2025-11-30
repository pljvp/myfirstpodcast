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
    
    def __init__(self, api_key: str, config: dict):
        super().__init__(api_key, config)
        self.api_url = "https://api.elevenlabs.io/v1/text-to-dialogue"
    
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
                    dialogue.append({
                        'voice_id': voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b'],
                        'text': ' '.join(current_text).strip()
                    })
                
                current_speaker = 'speaker_a'
                text = line.split(':', 1)[-1].strip().replace('**', '').strip()
                current_text = [text] if text else []
                
            elif is_speaker_b:
                if current_text and current_speaker:
                    dialogue.append({
                        'voice_id': voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b'],
                        'text': ' '.join(current_text).strip()
                    })
                
                current_speaker = 'speaker_b'
                text = line.split(':', 1)[-1].strip().replace('**', '').strip()
                current_text = [text] if text else []
                
            elif current_speaker:
                if not line.startswith('#') and not line.startswith('---'):
                    current_text.append(line)
        
        if current_text and current_speaker:
            voice_id = voice_ids['speaker_a'] if current_speaker == 'speaker_a' else voice_ids['speaker_b']
            dialogue.append({'voice_id': voice_id, 'text': ' '.join(current_text).strip()})
        
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
        project_name: Optional[str] = None
    ) -> Tuple[Optional[bytes], int]:
        """Generate audio using ElevenLabs API"""
        print(f"\n{'='*60}")
        print(f"TTS PROVIDER: ELEVENLABS")
        print(f"{'='*60}")
        
        dialogue = self.parse_script_to_dialogue(script, voice_ids)
        
        if not dialogue:
            print("\n[ERROR] Script format error - no Speaker A:/B: labels found")
            return None, 0
        
        # Add voice settings
        inputs = [{
            "text": seg['text'], 
            "voice_id": seg['voice_id'],
            "voice_settings": {"speed": speed}
        } for seg in dialogue]
        
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
