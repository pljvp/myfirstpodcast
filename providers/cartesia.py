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
        
    def _split_text_at_emotions(self, text):
        """
        Split text into segments at mid-sentence emotion tags.

        Args:
            text: Text that may contain [emotion] tags mid-sentence

        Returns:
            List of (emotions_list, clean_text) tuples
        """
        # Pattern to find emotion tags
        tag_pattern = r'\[([^\]]+)\]'

        # Find all tags and their positions
        tags_with_positions = [(m.group(1), m.start(), m.end()) for m in re.finditer(tag_pattern, text)]

        if not tags_with_positions:
            # No tags - return text with empty emotions
            return [([], text.strip())]

        # Check if tags are only at the start (before any substantial text)
        first_non_tag_char = 0
        temp_text = text
        while True:
            temp_text = temp_text.strip()
            if temp_text.startswith('['):
                end_bracket = temp_text.find(']')
                if end_bracket > 0:
                    temp_text = temp_text[end_bracket + 1:]
                    first_non_tag_char = text.find(temp_text.strip()) if temp_text.strip() else len(text)
                else:
                    break
            else:
                break

        # Get tags that are at the start (before any text content)
        start_tags = []
        for tag, start, end in tags_with_positions:
            if start < first_non_tag_char:
                start_tags.append(tag)

        # Get tags that are mid-sentence (after text content has started)
        mid_tags_with_positions = [(tag, start, end) for tag, start, end in tags_with_positions
                                    if start >= first_non_tag_char]

        if not mid_tags_with_positions:
            # All tags are at start - simple case
            emotions, clean_text = self._extract_emotions(text)
            return [(emotions, clean_text)] if clean_text.strip() else []

        # Split at mid-sentence tags
        segments = []
        current_pos = 0
        current_emotions = start_tags.copy()

        for tag, tag_start, tag_end in mid_tags_with_positions:
            # Get text before this tag
            text_before = text[current_pos:tag_start]
            # Remove any tags from text_before and get the clean text
            clean_before = re.sub(tag_pattern, '', text_before).strip()

            if clean_before:
                # Map emotions to Cartesia format
                mapped_emotions = []
                for t in current_emotions:
                    t_lower = t.lower()
                    if t_lower in self._get_emotion_map():
                        mapped_emotions.append(self._get_emotion_map()[t_lower])
                segments.append((mapped_emotions, clean_before))

            # This tag starts a new segment
            current_emotions = [tag]
            current_pos = tag_end

        # Get remaining text after last tag
        remaining_text = text[current_pos:]
        clean_remaining = re.sub(tag_pattern, '', remaining_text).strip()

        if clean_remaining:
            mapped_emotions = []
            for t in current_emotions:
                t_lower = t.lower()
                if t_lower in self._get_emotion_map():
                    mapped_emotions.append(self._get_emotion_map()[t_lower])
            segments.append((mapped_emotions, clean_remaining))

        return segments if segments else [([], text.strip())]

    def _get_emotion_map(self):
        """
        Return emotion mapping from script tags to Cartesia emotion names.

        Cartesia supports 60+ emotions directly. Most script tags can pass through.
        This map handles:
        1. Tags that match Cartesia emotions exactly (pass through)
        2. Tags that need mapping to closest Cartesia emotion
        3. ElevenLabs-only tags (return None to skip)

        Cartesia primary emotions (best results): neutral, angry, excited, content, sad, scared
        Full list: happy, excited, enthusiastic, elated, euphoric, triumphant, amazed,
        surprised, flirtatious, curious, content, peaceful, serene, calm, grateful,
        affectionate, trust, sympathetic, anticipation, mysterious, angry, mad, outraged,
        frustrated, agitated, threatened, disgusted, contempt, envious, sarcastic, ironic,
        sad, dejected, melancholic, disappointed, hurt, guilty, bored, tired, rejected,
        nostalgic, wistful, apologetic, hesitant, insecure, confused, resigned, anxious,
        panicked, alarmed, scared, neutral, proud, confident, distant, skeptical,
        contemplative, determined
        """
        return {
            # Direct matches (Cartesia supports these exactly)
            'excited': 'excited',
            'enthusiastic': 'enthusiastic',
            'happy': 'happy',
            'elated': 'elated',
            'euphoric': 'euphoric',
            'triumphant': 'triumphant',
            'amazed': 'amazed',
            'surprised': 'surprised',
            'curious': 'curious',
            'content': 'content',
            'peaceful': 'peaceful',
            'serene': 'serene',
            'calm': 'calm',
            'grateful': 'grateful',
            'affectionate': 'affectionate',
            'sympathetic': 'sympathetic',
            'mysterious': 'mysterious',
            'angry': 'angry',
            'mad': 'mad',
            'outraged': 'outraged',
            'frustrated': 'frustrated',
            'agitated': 'agitated',
            'disgusted': 'disgusted',
            'contempt': 'contempt',
            'envious': 'envious',
            'sarcastic': 'sarcastic',
            'ironic': 'ironic',
            'sad': 'sad',
            'dejected': 'dejected',
            'melancholic': 'melancholic',
            'disappointed': 'disappointed',
            'hurt': 'hurt',
            'guilty': 'guilty',
            'bored': 'bored',
            'tired': 'tired',
            'rejected': 'rejected',
            'nostalgic': 'nostalgic',
            'wistful': 'wistful',
            'apologetic': 'apologetic',
            'hesitant': 'hesitant',
            'insecure': 'insecure',
            'confused': 'confused',
            'resigned': 'resigned',
            'anxious': 'anxious',
            'panicked': 'panicked',
            'alarmed': 'alarmed',
            'scared': 'scared',
            'neutral': 'neutral',
            'proud': 'proud',
            'confident': 'confident',
            'distant': 'distant',
            'skeptical': 'skeptical',
            'contemplative': 'contemplative',
            'determined': 'determined',
            'flirtatious': 'flirtatious',

            # Mappings for common script tags to closest Cartesia emotion
            'thoughtful': 'contemplative',
            'analytical': 'contemplative',
            'pondering': 'contemplative',
            'reflective': 'contemplative',
            'cheerful': 'happy',
            'energetic': 'excited',
            'friendly': 'content',
            'warm': 'affectionate',
            'amused': 'happy',
            'satisfied': 'content',
            'hopeful': 'content',
            'encouraging': 'affectionate',
            'passionate': 'excited',
            'animated': 'excited',
            'playful': 'happy',
            'questioning': 'curious',
            'interested': 'curious',
            'uncertain': 'hesitant',
            'worried': 'anxious',
            'concerned': 'anxious',
            'nervous': 'anxious',
            'somber': 'sad',
            'emotional': 'sad',
            'annoyed': 'frustrated',
            'urgently': 'determined',
            'dramatically': 'excited',
            'intensely': 'determined',
            'pressing': 'determined',
            'emphatic': 'determined',
            'inspired': 'excited',
            'warmly': 'affectionate',
            'carefully': 'contemplative',
            'precisely': 'neutral',
            'understanding': 'sympathetic',
            'professional': 'neutral',
            'formal': 'neutral',
            'serious': 'neutral',
            'realizing': 'surprised',
            'impressed': 'amazed',

            # Vocal reactions - map to closest emotion
            'laughs': 'happy',
            'chuckles': 'happy',
            'giggles': 'happy',
            'chuckling': 'happy',
            'sighs': 'resigned',
            'gasps': 'surprised',
            'groans': 'frustrated',
            'hmm': 'contemplative',
            'uhh': 'hesitant',
            'gulps': 'scared',
            'quietly': 'calm',
            'sadly': 'sad',
            'shocked': 'alarmed',
            'wow': 'amazed',

            # Multi-word tags
            'switching gears': 'neutral',
            'building': 'anticipation',
            'building emotion': 'excited',
            'confirming': 'confident',
            'agreeing': 'content',
            'final push': 'determined',

            # ElevenLabs-only tags - return None (will be skipped)
            'interrupting': None,
            'overlapping': None,
            'interjecting': None,
            'fast-paced': None,
            'slowly': None,
            'pause': None,
            'whispers': None,
            'shouting': None,
            'loudly': None,
            'hesitates': None,
        }

    def parse_script_to_dialogue(self, script, voice_ids):
        """Parse script into Cartesia dialogue format

        Handles mid-sentence emotion tags by splitting into multiple segments.
        Same speaker can have consecutive segments with different emotions.

        Args:
            script: Raw script text with Speaker A:/B: and [tags]
            voice_ids: Dict with speaker_a and speaker_b voice IDs

        Returns:
            List of dialogue items for Cartesia API
        """
        dialogue = []
        lines = script.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Determine speaker
            speaker = None
            text_content = None

            if line.startswith('Speaker A:'):
                speaker = 'speaker_a'
                text_content = line[10:].strip()
            elif line.startswith('Speaker B:'):
                speaker = 'speaker_b'
                text_content = line[10:].strip()

            if speaker and text_content:
                # Split text at mid-sentence emotion tags
                segments = self._split_text_at_emotions(text_content)

                for emotions, clean_text in segments:
                    if clean_text.strip():
                        dialogue.append(self._create_segment(
                            speaker,
                            clean_text,
                            emotions,
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

        # Use centralized emotion map
        emotion_map = self._get_emotion_map()

        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in emotion_map:
                emotions.append(emotion_map[tag_lower])
            # Note: Tags not in map are ignored for Cartesia
            # They may be valid for ElevenLabs

        # Remove tags from text
        clean_text = re.sub(r'\[([^\]]+)\]', '', text).strip()

        return emotions, clean_text
    
    def _create_segment(self, speaker, text, emotions, voice_ids):
        """Create a Cartesia dialogue segment

        Args:
            speaker: 'speaker_a' or 'speaker_b'
            text: Clean dialogue text
            emotions: List of emotion strings (already mapped to Cartesia format)
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

        # Cartesia expects emotion as ARRAY
        # Use up to 2 emotions for richer expression
        if emotions:
            unique_emotions = list(dict.fromkeys(emotions))  # Remove duplicates, preserve order
            segment["__experimental_controls"]["emotion"] = unique_emotions[:2]

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
        
        # Check if speed is a dict (per-speaker) or float (single speed)
        speed_is_dict = isinstance(speed, dict)
        
        if speed_is_dict:
            # tune_audio mode with per-speaker speeds
            cartesia_speeds = {}
            for speaker in ['speaker_a', 'speaker_b']:
                spk_speed = speed.get(speaker, 1.0)
                cartesia_speeds[speaker] = (spk_speed - 1.0) * 2.0
                cartesia_speeds[speaker] = max(-1.0, min(1.0, cartesia_speeds[speaker]))
            
            print(f"\n{'='*60}")
            print(f"TTS PROVIDER: CARTESIA")
            print(f"Model: sonic-english")
            print(f"Per-speaker speeds:")
            print(f"  Speaker A: {speed['speaker_a']} → {cartesia_speeds['speaker_a']:.2f} (Cartesia)")
            print(f"  Speaker B: {speed['speaker_b']} → {cartesia_speeds['speaker_b']:.2f} (Cartesia)")
            print(f"{'='*60}")
        else:
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
            
            # Determine which speaker this segment is for
            voice_id = segment['voice_id']
            speaker = None
            for spk in ['speaker_a', 'speaker_b']:
                config = self._get_voice_config(spk, self.language)
                if config['id'] == voice_id:
                    speaker = spk
                    break
            
            if use_config_speeds:
                # PIPELINE MODE: Multiply by config defaults
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
                if speed_is_dict:
                    # Per-speaker speeds provided
                    if speaker:
                        segment["__experimental_controls"]["speed"] = cartesia_speeds[speaker]
                    else:
                        # Fallback to speaker_a speed
                        segment["__experimental_controls"]["speed"] = cartesia_speeds['speaker_a']
                else:
                    # Single speed for all
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
        
        # Combine audio chunks with crossfading to eliminate clicks
        if audio_chunks:
            import numpy as np
            from pydub import AudioSegment
            import io
            
            # Convert each chunk to AudioSegment first
            audio_segments = []
            for chunk in audio_chunks:
                # Convert raw bytes to float32 numpy array
                pcm_float_array = np.frombuffer(chunk, dtype=np.float32)
                
                # Convert float32 to int16
                pcm_int16_array = (pcm_float_array * 32767).astype(np.int16)
                
                # Create AudioSegment
                segment = AudioSegment(
                    data=pcm_int16_array.tobytes(),
                    sample_width=2,
                    frame_rate=44100,
                    channels=1
                )
                audio_segments.append(segment)
            
            # Concatenate with 10ms crossfade to eliminate clicks
            combined_audio_segment = audio_segments[0]
            for next_segment in audio_segments[1:]:
                combined_audio_segment = combined_audio_segment.append(next_segment, crossfade=10)
            
            # Export to MP3
            mp3_buffer = io.BytesIO()
            combined_audio_segment.export(mp3_buffer, format="mp3", bitrate="192k")
            combined_audio = mp3_buffer.getvalue()
            
            return combined_audio, total_chars
                
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
