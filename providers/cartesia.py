"""
Cartesia TTS Provider
Handles Cartesia Sonic API for podcast generation
"""

import requests
import re
from pathlib import Path


class CartesiaProvider:
    """Cartesia TTS provider using Sonic model"""
    
    PROVIDER_TAG = "CRTS"
    
    def __init__(self, api_key, config):
        """Initialize Cartesia provider
        
        Args:
            api_key: Cartesia API key
            config: Provider configuration from podcast_config.json
        """
        self.api_key = api_key
        self.config = config
        self.base_url = "https://api.cartesia.ai"
        
    def parse_script_to_dialogue(self, script, voice_ids):
        """Parse script into Cartesia dialogue format
        
        Args:
            script: Raw script text with Speaker A:/B: and [tags]
            voice_ids: Dict with speaker_a and speaker_b voice IDs
            
        Returns:
            List of dialogue items for Cartesia API
        """
        dialogue = []
        lines = script.split('\n')
        
        current_speaker = None
        current_text = []
        current_emotions = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for speaker labels
            if line.startswith('Speaker A:'):
                # Save previous segment
                if current_speaker and current_text:
                    dialogue.append(self._create_segment(
                        current_speaker,
                        ' '.join(current_text),
                        current_emotions,
                        voice_ids
                    ))
                
                current_speaker = 'speaker_a'
                current_text = []
                current_emotions = []
                
                # Get text after "Speaker A:"
                text = line[10:].strip()
                if text:
                    emotions, clean_text = self._extract_emotions(text)
                    current_text.append(clean_text)
                    current_emotions.extend(emotions)
                    
            elif line.startswith('Speaker B:'):
                # Save previous segment
                if current_speaker and current_text:
                    dialogue.append(self._create_segment(
                        current_speaker,
                        ' '.join(current_text),
                        current_emotions,
                        voice_ids
                    ))
                
                current_speaker = 'speaker_b'
                current_text = []
                current_emotions = []
                
                # Get text after "Speaker B:"
                text = line[10:].strip()
                if text:
                    emotions, clean_text = self._extract_emotions(text)
                    current_text.append(clean_text)
                    current_emotions.extend(emotions)
                    
            else:
                # Continuation of current speaker
                if current_speaker:
                    emotions, clean_text = self._extract_emotions(line)
                    current_text.append(clean_text)
                    current_emotions.extend(emotions)
        
        # Don't forget last segment
        if current_speaker and current_text:
            dialogue.append(self._create_segment(
                current_speaker,
                ' '.join(current_text),
                current_emotions,
                voice_ids
            ))
        
        return dialogue
    
    def _extract_emotions(self, text):
        """Extract emotion tags from text
        
        Args:
            text: Text potentially containing [emotion] tags
            
        Returns:
            Tuple of (emotions_list, clean_text)
        """
        emotions = []
        
        # Find all [tag] patterns
        tags = re.findall(r'\[([^\]]+)\]', text)
        
        # Map common tags to Cartesia emotions
        # Cartesia supports: high, low, highest, lowest (NOT medium!)
        emotion_map = {
            'excited': 'positivity:high',
            'enthusiastic': 'positivity:high',
            'happy': 'positivity:high',
            'curious': 'curiosity:high',
            'questioning': 'curiosity:high',
            'thoughtful': 'curiosity:low',
            'analytical': 'curiosity:low',
            'surprised': 'surprise:high',
            'amazed': 'surprise:high',
            'worried': 'anger:low',
            'concerned': 'curiosity:low',
            'laughs': 'positivity:high',
            'chuckles': 'positivity:low',
        }
        
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in emotion_map:
                emotions.append(emotion_map[tag_lower])
        
        # Remove tags from text
        clean_text = re.sub(r'\[([^\]]+)\]', '', text).strip()
        
        return emotions, clean_text
    
    def _create_segment(self, speaker, text, emotions, voice_ids):
        """Create a Cartesia dialogue segment
        
        Args:
            speaker: 'speaker_a' or 'speaker_b'
            text: Clean dialogue text
            emotions: List of emotion strings
            voice_ids: Voice ID mapping
            
        Returns:
            Dict in Cartesia format
        """
        voice_id = voice_ids[speaker]
        
        segment = {
            "voice_id": voice_id,
            "transcript": text,
            "__experimental_controls": {}
        }
        
        # CRITICAL FIX: Cartesia expects emotion as ARRAY, not string
        if emotions:
            # Take the first emotion (or could combine them)
            segment["__experimental_controls"]["emotion"] = [emotions[0]]
        
        return segment
    
    def generate_audio(self, script, voice_ids, mode='production', speed=1.0, project_name=None):
        """Generate audio using Cartesia API
        
        Args:
            script: Formatted script text
            voice_ids: Dict with speaker_a and speaker_b IDs
            mode: 'prototype' or 'production' (ignored - Cartesia always full quality)
            speed: Speech speed (0.7-1.2)
            project_name: Project name for debug files
            
        Returns:
            Tuple of (audio_data, character_count)
        """
        # Parse script
        dialogue = self.parse_script_to_dialogue(script, voice_ids)
        
        if not dialogue:
            print("[ERROR] No dialogue segments parsed from script")
            return None, 0
        
        # Convert ElevenLabs speed range (0.7-1.2) to Cartesia range (-1.0 to 1.0)
        # ElevenLabs: 0.7 = slow, 1.0 = normal, 1.2 = fast
        # Cartesia: -1.0 = slow, 0.0 = normal, 1.0 = fast
        cartesia_speed = (speed - 1.0) * 2.0  # Maps 0.7→-0.6, 1.0→0.0, 1.2→0.4
        cartesia_speed = max(-1.0, min(1.0, cartesia_speed))  # Clamp to valid range
        
        print(f"\n{'='*60}")
        print(f"TTS PROVIDER: CARTESIA")
        print(f"Model: sonic-english")
        print(f"Speed: {speed} (ElevenLabs) → {cartesia_speed:.2f} (Cartesia)")
        print(f"{'='*60}")
        
        # Apply speed to all segments
        for segment in dialogue:
            if "__experimental_controls" not in segment:
                segment["__experimental_controls"] = {}
            segment["__experimental_controls"]["speed"] = cartesia_speed
        
        total_chars = sum(len(seg['transcript']) for seg in dialogue)
        print(f"[DEBUG] Total dialogue: {total_chars} characters, {len(dialogue)} segments")
        
        # Generate audio segments
        audio_chunks = []
        
        for i, segment in enumerate(dialogue, 1):
            char_count = len(segment['transcript'])
            emotion_info = segment.get('__experimental_controls', {}).get('emotion', ['neutral'])
            print(f"[Segment {i}/{len(dialogue)}] {char_count} chars {emotion_info}")
            
            # Save debug info
            if project_name:
                debug_dir = Path(f"./projects/{project_name}/debug")
                debug_dir.mkdir(parents=True, exist_ok=True)
                
                import json
                debug_file = debug_dir / f"chunk_{i}_CRTS_content.json"
                with open(debug_file, 'w') as f:
                    json.dump({
                        'segment_number': i,
                        'character_count': char_count,
                        'transcript': segment['transcript'],
                        'voice_id': segment['voice_id'],
                        'controls': segment.get('__experimental_controls', {})
                    }, f, indent=2)
            
            # Call Cartesia API
            url = f"{self.base_url}/tts/bytes"
            headers = {
                "X-API-Key": self.api_key,
                "Cartesia-Version": "2024-06-10",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model_id": "sonic-english",
                "transcript": segment['transcript'],
                "voice": {
                    "mode": "id",
                    "id": segment['voice_id'],
                    "__experimental_controls": segment.get('__experimental_controls', {})
                },
                "output_format": {
                    "container": "mp3",
                    "encoding": "mp3",
                    "sample_rate": 44100
                }
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    audio_chunks.append(response.content)
                else:
                    print(f"[ERROR] Status {response.status_code}: {response.text}")
                    return None, 0
                    
            except Exception as e:
                print(f"[ERROR] {type(e).__name__}: {e}")
                return None, 0
        
        # Combine audio chunks
        if audio_chunks:
            combined_audio = b''.join(audio_chunks)
            return combined_audio, total_chars
        else:
            return None, 0

    
    def _save_debug_chunk(self, chunk_content: dict, chunk_num: int, project_name: str):
        """Save chunk for debugging with CRTS tag"""
        from pathlib import Path
        import json
        
        debug_path = Path(f"./projects/{project_name}/debug")
        debug_path.mkdir(parents=True, exist_ok=True)
        
        debug_file = debug_path / f"chunk_{chunk_num}_CRTS_content.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_content, f, indent=2, ensure_ascii=False)
