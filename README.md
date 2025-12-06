# AI Podcast Pipeline

Generate professional podcasts with Claude research + multi-provider TTS audio.

## Features

- **Multi-Provider TTS:** ElevenLabs or Cartesia (Sonic)
- **Claude AI Research:** Web search + your documents
- **Multi-Language:** German, English, Dutch
- **Smart Script Detection:** Reuse existing scripts
- **Source Documents:** PDFs, Word, PowerPoint integration
- **Post-Processing Tools:** Translation, speed tuning
- **Clean Audio:** PCM-based concatenation (no artifacts)

## Quick Start

### **1. Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

### **2. Install ffmpeg (Required for Audio Processing):**

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
# Option 1: Chocolatey (recommended if installed)
choco install ffmpeg

# Option 2: Scoop (if installed)
scoop install ffmpeg

# Option 3: Manual - Download from https://ffmpeg.org/download.html, extract, add bin folder to PATH
```

### **3. Create `.env` file:**
```bash
cd config
nano .env  # or notepad .env on Windows
```

Add your API keys:
```
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
CARTESIA_API_KEY=...
```

### **4. Configure voices in `podcast_config.json`**

Update voice IDs for your chosen providers and languages.

### **5. Run pipeline:**
```bash
python podcast_pipeline.py
```

### **6. Follow prompts** for project setup, provider selection, and generation

[Rest of README content continues as before...]
