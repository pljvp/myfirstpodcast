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
    
    def __init__(self, api_key, config, language='english'):
        """Initialize Cartesia provider
        
        Args:
            api_key: Cartesia API key
            config: Provider configuration from podcast_config.json
            language: Language code (english, german, dutch)
        """
        self.api_key = api_key
        self.config = config
        self.language = language
        self.base_url = "https://api.cartesia.ai"
    
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
        
        # COMPREHENSIVE Cartesia emotion mapping (50+ tags)
        # Cartesia supports 5 emotions with intensity: positivity, curiosity, surprise, sadness, anger
        # Intensities: highest, high, low, lowest
        emotion_map = {
            # Positive/Excited
            'excited': 'positivity:high',
            'enthusiastic': 'positivity:high',
            'happy': 'positivity:high',
            'cheerful': 'positivity:high',
            'energetic': 'positivity:high',
            'friendly': 'positivity:low',
            'warm': 'positivity:low',
            'amused': 'positivity:low',
            'satisfied': 'positivity:low',
            'hopeful': 'positivity:low',
            'proud': 'positivity:high',
            
            # Curious/Thoughtful
            'curious': 'curiosity:high',
            'questioning': 'curiosity:high',
            'interested': 'curiosity:high',
            'thoughtful': 'curiosity:low',
            'analytical': 'curiosity:low',
            'pondering': 'curiosity:low',
            'confused': 'curiosity:high',
            'hesitates': 'curiosity:low',
            'explaining': 'curiosity:low',
            'clarifying': 'curiosity:low',
            'carefully': 'curiosity:low',
            'precisely': 'curiosity:low',
            
            # Surprised
            'surprised': 'surprise:high',
            'shocked': 'surprise:highest',
            'amazed': 'surprise:high',
            'gasps': 'surprise:high',
            'wow': 'surprise:high',
            'realizing': 'surprise:low',
            'impressed': 'surprise:low',
            
            # Concerned/Sad
            'worried': 'sadness:low',
            'concerned': 'sadness:low',
            'nervous': 'sadness:low',
            'anxious': 'sadness:low',
            'disappointed': 'sadness:high',
            'sighs': 'sadness:low',
            'quietly': 'sadness:low',
            'sadly': 'sadness:high',
            'somber': 'sadness:low',
            
            # Skeptical/Frustrated
            'skeptical': 'anger:low',
            'frustrated': 'anger:low',
            'annoyed': 'anger:low',
            'angry': 'anger:high',
            'groans': 'anger:low',
            'urgently': 'anger:low',
            'dramatically': 'anger:low',
            'intensely': 'anger:high',
            'pressing': 'anger:low',
            
            # Laughter
            'laughs': 'positivity:high',
            'chuckles': 'positivity:low',
            'giggles': 'positivity:high',
            
            # Vocal reactions
            'hmm': 'curiosity:low',
            'uhh': 'curiosity:low',
            'gulps': 'surprise:low',
            
            # Additional nuanced tags
            'professional': 'curiosity:low',
            'formal': 'curiosity:low',
            'casual': 'positivity:low',
            'playful': 'positivity:high',
            'serious': 'curiosity:low',
            'determined': 'anger:low',
            'confident': 'positivity:low',
            'uncertain': 'curiosity:high',
        }
        
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in emotion_map:
                emotions.append(emotion_map[tag_lower])
            # Note: Tags like [interrupting], [fast-paced] are kept in text but not mapped
            # They're valid for ElevenLabs and future Cartesia support
        
        # Remove tags from text
        clean_text = re.sub(r'\[([^\]]+)\]', '', text).strip()
        
        return emotions, clean_text
    
    def _create_segment(self, speaker, text, emotions, voice_ids):
        """Create a Cartesia dialogue segment
        
        Args:
            speaker: 'speaker_a' or 'speaker_b'
            text: Clean dialogue text
            emotions: List of emotion strings
            voice_ids: Voice ID mapping (can be string or dict with 'id' key)
            
        Returns:
            Dict in Cartesia format
        """
        voice_config = voice_ids[speaker]
        
        # Extract ID - handle both formats (string or dict)
        if isinstance(voice_config, dict):
            voice_id = voice_config.get('id', voice_config)
        else:
            voice_id = voice_config
        
        segment = {
            "voice_id": voice_id,  # Must be STRING for Cartesia API
            "transcript": text,
            "__experimental_controls": {}
        }
        
        # CRITICAL FIX: Cartesia expects emotion as ARRAY, not string
        if emotions:
            # Take the first emotion (or could combine them)
            segment["__experimental_controls"]["emotion"] = [emotions[0]]
        
        return segment
    
    def generate_audio(self, script, voice_ids, mode='production', speed=1.0, project_name=None, use_config_speeds=True):
        """Generate audio using Cartesia API
        
        Args:
            script: Formatted script text
            voice_ids: Dict with speaker_a and speaker_b IDs
            mode: 'prototype' or 'production' (ignored - Cartesia always full quality)
            speed: Speech speed (0.7-1.2)
            project_name: Project name for debug files
            use_config_speeds: If True, multiply speed by per-voice defaults (pipeline mode)
                               If False, use speed directly (tune_audio mode)
            
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
        print(f"Base speed: {speed} (ElevenLabs) → {cartesia_speed:.2f} (Cartesia)")
        
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
        
        # Apply speed to all segments WITH PER-VOICE DEFAULTS (if enabled)
        for segment in dialogue:
            if "__experimental_controls" not in segment:
                segment["__experimental_controls"] = {}
            
            if use_config_speeds:
                # PIPELINE MODE: Multiply by config defaults
                # Determine which speaker this segment is for
                voice_id = segment['voice_id']
                speaker = None
                for spk in ['speaker_a', 'speaker_b']:
                    config = self._get_voice_config(spk, self.language)
                    if config['id'] == voice_id:
                        speaker = spk
                        break
                
                # Get per-voice default speed
                if speaker:
                    voice_cfg = self._get_voice_config(speaker, self.language)
                    voice_default = voice_cfg['default_speed']
                    
                    # Combine: base_speed * voice_default
                    final_speed = speed * voice_default
                    
                    # Convert to Cartesia range
                    cartesia_final = (final_speed - 1.0) * 2.0
                    cartesia_final = max(-1.0, min(1.0, cartesia_final))
                    
                    segment["__experimental_controls"]["speed"] = cartesia_final
                else:
                    # Fallback if speaker not found
                    segment["__experimental_controls"]["speed"] = cartesia_speed
            else:
                # TUNE_AUDIO MODE: Use speed directly (ignore config defaults)
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
                    "container": "raw",
                    "encoding": "pcm_f32le",
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
        
        # Combine audio chunks (PCM is safe to concatenate)
        if audio_chunks:
            combined_pcm = b''.join(audio_chunks)
            
            # Convert float32 PCM to MP3 using pydub
            # CRITICAL: Cartesia returns pcm_f32le (float), but pydub expects int PCM
            try:
                import numpy as np
                from pydub import AudioSegment
                import io
                
                # Step 1: Convert raw bytes to float32 numpy array
                pcm_float_array = np.frombuffer(combined_pcm, dtype=np.float32)
                
                # Step 2: Convert float32 (-1.0 to 1.0) to int16 (-32768 to 32767)
                # This is the critical conversion - pydub doesn't support float PCM directly
                pcm_int16_array = (pcm_float_array * 32767).astype(np.int16)
                
                # Step 3: Create AudioSegment from int16 PCM
                audio = AudioSegment(
                    data=pcm_int16_array.tobytes(),
                    sample_width=2,  # 16-bit = 2 bytes (NOT 4!)
                    frame_rate=44100,
                    channels=1
                )
                
                # Step 4: Export to MP3
                mp3_buffer = io.BytesIO()
                audio.export(mp3_buffer, format="mp3", bitrate="192k")
                combined_audio = mp3_buffer.getvalue()
                
                return combined_audio, total_chars
                
            except ImportError as e:
                print(f"[ERROR] Missing required library: {e}")
                print("[ERROR] Install required packages:")
                print("[ERROR]   pip install numpy pydub")
                print("[ERROR]   (and ensure ffmpeg is installed)")
                return combined_pcm, total_chars
            except Exception as e:
                print(f"[ERROR] PCM to MP3 conversion failed: {e}")
                import traceback
                traceback.print_exc()
                print("[WARNING] Returning raw float32 PCM instead of MP3")
                return combined_pcm, total_chars
        else:
            return None, 0
    
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

    
    def _save_debug_chunk(self, chunk_content: dict, chunk_num: int, project_name: str):
        """Save chunk for debugging with CRTS tag"""
        from pathlib import Path
        import json
        
        debug_path = Path(f"./projects/{project_name}/debug")
        debug_path.mkdir(parents=True, exist_ok=True)
        
        debug_file = debug_path / f"chunk_{chunk_num}_CRTS_content.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_content, f, indent=2, ensure_ascii=False)
