# Installation & Setup

## Prerequisites
- Python 3.8+
- ffmpeg (for audio processing)

## Quick Install

```bash
# 1. Install Python dependencies
pip install -r requirements.txt
<<<<<<< HEAD
```
or 
```bash
# Install requirements using the default Python
py -m pip install -r requirements.txt
```

=======
>>>>>>> multi-call-scaling-01Dh5pjGvw4oADjWQdZgFFoX

# 2. Install ffmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: choco install ffmpeg

# 3. Configure API keys
cp config/.env.template config/.env
# Edit config/.env with your keys:
# ANTHROPIC_API_KEY=sk-ant-...
# ELEVENLABS_API_KEY=sk_...
# CARTESIA_API_KEY=...

# 4. Configure voice IDs in config/podcast_config.json
# 2 providers × 3 languages × 2 speakers = 12 voice IDs
```

## Get API Keys
- Anthropic: https://console.anthropic.com/
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- Cartesia: https://cartesia.ai/

## Test Installation

```bash
python podcast_pipeline.py
# Project: test
# Follow prompts for a quick 2-min test
```

## Daily Usage

```bash
python podcast_pipeline.py    # Generate podcasts
python tune_audio.py          # Adjust speaker speeds
python translate_script.py    # Translate scripts
```

## Update Dependencies

After pulling new code:
```bash
pip install -r requirements.txt
```

## Troubleshooting

**Check dependencies:**
```bash
pip list | grep -E "anthropic|pydub|cartesia|PyYAML"
ffmpeg -version
```

**Debug files:** `projects/{project}/debug/`
