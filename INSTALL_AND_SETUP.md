# 📦 AI Podcast Pipeline - Installation & Setup

Complete guide for first-time installation, daily usage, and updates.

---

## 📋 **Table of Contents**

1. [First-Time Installation](#first-time-installation)
2. [Daily Usage](#daily-usage)
3. [Updating Existing Installation](#updating-existing-installation)
4. [Post-Processing Tools](#post-processing-tools)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 **First-Time Installation**

### **Prerequisites**
- Python 3.8+
- Git (optional)

### **Step 1: Get the Code**

**Option A - Clone:**
```bash
git clone https://github.com/yourusername/myfirstpodcast.git
cd myfirstpodcast
```

**Option B - Download ZIP:**
```bash
unzip myfirstpodcast.zip
cd myfirstpodcast
```

---

### **Step 2: Install Python Dependencies**

```bash
pip install -r requirements.txt
```
or 
```bash
# Install requirements using the default Python
py -m pip install -r requirements.txt
```


**Includes:**
- `anthropic` - Claude API
- `requests` - HTTP requests
- `python-dotenv` - Environment variables
- `cartesia` - Cartesia TTS
- `pydub` - Audio processing
- `python-docx`, `PyPDF2`, `python-pptx` (optional - document reading)

---

### **Step 3: Install ffmpeg (System Dependency)**

**Required for:** Cartesia audio processing (PCM → MP3)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```powershell
# Option 1: Chocolatey (recommended)
choco install ffmpeg

# Option 2: Scoop
scoop install ffmpeg

# Option 3: Manual
# Download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg
# Add C:\ffmpeg\bin to PATH
```

**Verify:**
```bash
ffmpeg -version
```

---

### **Step 4: Configure API Keys**

**Create `.env` file:**
```bash
cd config
cp .env.template .env  # or create manually
nano .env  # or notepad .env on Windows
```

**Add your API keys:**
```
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
CARTESIA_API_KEY=...
```

**Get API keys:**
- Anthropic: https://console.anthropic.com/
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- Cartesia: https://cartesia.ai/

---

### **Step 5: Configure Voice IDs**

**Edit `config/podcast_config.json`:**
```bash
nano config/podcast_config.json
```

**Replace voice IDs for both providers:**

```json
{
  "providers": {
    "elevenlabs": {
      "voices": {
        "german": {
          "speaker_a_female": "YOUR_ELEVENLABS_VOICE_ID",
          "speaker_b_male": "YOUR_ELEVENLABS_VOICE_ID"
        },
        "english": { ... },
        "dutch": { ... }
      }
    },
    "cartesia": {
      "voices": {
        "german": {
          "speaker_a_female": "YOUR_CARTESIA_VOICE_ID",
          "speaker_b_male": "YOUR_CARTESIA_VOICE_ID"
        },
        "english": { ... },
        "dutch": { ... }
      }
    }
  }
}
```

**Get voice IDs:**
- ElevenLabs: https://elevenlabs.io/app/voice-library
- Cartesia: https://cartesia.ai/voices

**Total:** 12 voice IDs (2 providers × 3 languages × 2 speakers)

---

### **Step 6: Test Installation**

```bash
python podcast_pipeline.py
```

**Create a test podcast:**
```
Project name: test
Scenario: 3. Movie scene analysis
Topic: 4. My Neighbor Totoro
Duration: 2 minutes
Language: German
Provider: Cartesia
Mode: Prototype
```

**If successful:** ✅ You're ready!

---

## 🎙️ **Daily Usage**

### **Creating a Podcast**

```bash
python podcast_pipeline.py
```

**Follow prompts:**
1. **Project name:** `BACnet` (or any name)
2. **Topic:** `BACnet protocol in building automation`
3. **Duration:** `15 minutes`
4. **Style:** `1. Dynamic, friendly science`
5. **Language:** `1. Deutsch (German)`
6. **Provider:** `2. Cartesia` or `1. ElevenLabs`
7. **Mode:** `2. Production` or `1. Prototype`
8. **Speed:** `[Enter]` for default or `0.7-1.2`

**Output:**
```
projects/BACnet/
├── scripts/
│   └── BACnet_DE_2025-12-06_14-30_CRTS_draft1.txt
├── audio/
│   └── BACnet_de_2025-12-06_CRTS_PRODUCTION.mp3
└── sources/
    └── BACnet_sources.txt
```

---

### **Test Mode (Voice Tuning)**

**Quick 1-1.5 min tests:**

```bash
python podcast_pipeline.py
```

**Project name:** `test` (exactly "test")

**Select scenario:**
```
1. Road trip argument
2. Cooking disaster
3. Movie scene analysis
4. Random scenario
```

**Output:**
```
test_de_2025-12-06_mvie-totr_CRTS_OS1.00_MS1.00_FS1.00_PROTOTYPE.mp3
```

**Use for:** Testing voices, speeds, emotions

---

## 🔄 **Updating Existing Installation**

### **Method 1: Using smart_update.py (Recommended)**

**Step 1: Get update files**
```bash
# Download from Claude or GitHub
# Place *_FIXED.py and *_UPDATED.* files in root
```

**Step 2: Run update script**
```bash
python smart_update.py
```

**What it does:**
1. ✅ Backs up all your data (.env, configs, templates, projects)
2. ✅ Updates core files (pipeline, providers, utilities)
3. ✅ Checks ffmpeg installation
4. ✅ Installs new Python dependencies
5. ✅ Restores your data
6. ✅ Cleans up temporary files
7. ✅ Shows dependency status

**Output example:**
```
📦 BACKING UP YOUR DATA...
  → API keys & config...
  → Research templates...
  → Project contexts...

✅ Backed up to: .update_backup_20251206_143022

📁 Updating core files...
  ✅ Found: podcast_pipeline_FIXED.py
     → Updated: podcast_pipeline.py
  ✅ Found: cartesia_FIXED.py
     → Updated: providers/cartesia.py

📦 Installing Python dependencies...
  Running: pip install -r requirements.txt
  ✅ Python dependencies installed

📦 RESTORING YOUR DATA...
  → API keys...
  → Research templates...
  → Project contexts...

🧹 Cleaning up temporary files from root...
  ✅ Removed: podcast_pipeline_FIXED.py
  ✅ Removed: cartesia_FIXED.py

📋 Dependency Status:
  ✅ pydub           installed (required)
  ✅ anthropic       installed (required)
  ✅ cartesia        installed (required)
  ✅ ffmpeg          installed (required)

✅ UPDATE COMPLETE

✅ All systems ready!

Run: python podcast_pipeline.py
```

---

### **Method 2: Using smart_update.sh (Legacy)**

**Keep for bootstrapping the Python version:**

```bash
# Copy new smart_update_FIXED.py to root
cp outputs/smart_update_FIXED.py .

# Use .sh to deploy it
./smart_update.sh

# From now on, use Python version
python smart_update.py
```

**⚠️ REMINDER: Manually remove smart_update.sh after switching to .py**

---

### **Manual Update (If Needed)**

```bash
# 1. Backup
cp podcast_pipeline.py podcast_pipeline.py.backup

# 2. Copy files
cp outputs/podcast_pipeline_FIXED.py podcast_pipeline.py
cp outputs/cartesia_FIXED.py providers/cartesia.py
cp outputs/requirements_UPDATED.txt requirements.txt

# 3. Install dependencies
pip install -r requirements.txt

# 4. Clean up
rm *_FIXED.py *_UPDATED.*
```

---

## 🛠️ **Post-Processing Tools**

### **tune_audio.py - Adjust Speaker Speeds**

```bash
python tune_audio.py
```

**Workflow:**
```
Available scripts:
  1. BACnet_DE_2025-12-06_CRTS_draft1.txt

Select: 1

[INFO] Detected provider: CARTESIA
[INFO] Default speed: 1.0

Speaker A speed (0.7-1.2): 0.95
Speaker B speed (0.7-1.2): 1.05

[Processing 50 segments...]
✅ Generated: BACnet_A0.95_B1.05_de_2025-12-06_CRTS_TUNED.mp3
```

**Features:**
- Auto-detects provider from filename
- Per-speaker speed control
- Segment-by-segment processing
- No script regeneration needed

---

### **translate_script.py - Translate Scripts**

```bash
python translate_script.py
```

**Workflow:**
```
Available scripts:
  1. BACnet_DE_2025-12-06_CRTS_draft1.txt

Select: 1

Source: German (DE)

Target language:
  1. English
  2. Nederlands

Select: 1

[Claude translating...]
✅ Translated: BACnet_EN_2025-12-06_CRTS_draft1.txt
```

**Features:**
- Preserves emotion tags
- Maintains provider tag
- Natural translation via Claude

---

## 🎯 **Advanced Features**

### **Research Contexts**

**Global:** `templates/research_contexts/default.txt`  
**Project-specific:** `projects/{project}/sources/research_context.txt`

**Customize research per project:**
```bash
cd projects/BACnet/sources
nano research_context.txt
```

Add specific instructions:
```
Focus on:
- Technical specifications
- Industry standards
- Real-world implementations

Avoid:
- Marketing materials
- Unverified claims
```

---

### **Source Documents**

**Add your documents:**
```bash
cd projects/BACnet/sources
# Copy PDFs, Word docs, PowerPoints here
```

**Supported:**
- PDF (`.pdf`)
- Word (`.docx`)
- PowerPoint (`.pptx`)
- Text (`.txt`, `.md`)

**Claude automatically:**
- Extracts text
- Analyzes content
- Integrates with web research

---

### **Multi-Draft Workflow**

**Scripts auto-increment:**
```
BACnet_DE_2025-12-06_CRTS_draft1.txt
BACnet_DE_2025-12-06_CRTS_draft2.txt  ← After revision
BACnet_DE_2025-12-06_CRTS_draft3.txt  ← After another
```

**Pipeline detects existing scripts and offers to reuse**

---

### **Speed Settings**

**Unified interface (0.7-1.2 for all providers):**

| Value | Description | ElevenLabs | Cartesia (internal) |
|-------|-------------|------------|---------------------|
| 0.7 | Slow | 0.7 | -0.6 |
| 1.0 | Normal | 1.0 | 0.0 |
| 1.05 | Default | 1.05 | 0.1 |
| 1.2 | Fast | 1.2 | 0.4 |

**Cartesia speeds auto-convert internally**

---

## 🔍 **Troubleshooting**

### **Audio Artifacts / Cropped Sentences**

**Fixed in latest version!** Cartesia uses PCM concatenation.

**Verify:**
```bash
pip show pydub
ffmpeg -version
```

**If missing:**
```bash
pip install pydub
# Install ffmpeg (see Step 3 above)
```

---

### **"Module 'providers' not found"**

```bash
ls -la providers/
# Should show: __init__.py, base.py, elevenlabs.py, cartesia.py
```

**If missing:** Re-extract or re-clone repository

---

### **Provider Detection Issues**

**Check filename has provider tag:**
- `_CRTS_` = Cartesia
- `_11LB_` = ElevenLabs

**Scripts must follow naming convention**

---

### **Speed Settings Not Applied**

**tune_audio.py processes segments individually**

**Verify:**
- Console shows per-segment speeds
- Voice IDs configured in `podcast_config.json`

---

### **Single Voice Output (Dutch Bug)**

**If script has `**Speaker A:**` (bold markdown):**

```bash
# Fix script manually
sed -i 's/\*\*Speaker A:\*\*/Speaker A:/g' script.txt
sed -i 's/\*\*Speaker B:\*\*/Speaker B:/g' script.txt
```

**Templates updated to prevent this**

---

## 📊 **Provider Comparison**

| Feature | ElevenLabs | Cartesia |
|---------|------------|----------|
| **Emotions** | Full dynamics | Optimized subset |
| **Interruptions** | `[interrupting]` tag | Em dash (—) |
| **Speed** | Fast | Faster |
| **Cost** | $5-330/mo | ~$0.05/min |
| **Quality** | Excellent | Excellent |
| **Audio** | MP3 direct | PCM → MP3 (cleaner) |

---

## 📂 **File Naming Conventions**

### **Scripts:**
```
{project}_{LANG}_{DATE}_{TIME}_{PROVIDER}_draft{N}.txt

Examples:
BACnet_DE_2025-12-06_14-30_CRTS_draft1.txt
BACnet_EN_2025-12-06_15-00_11LB_draft1.txt
```

### **Audio:**
```
{project}_{lang}_{date}_{provider}_{MODE}.mp3

Examples:
BACnet_de_2025-12-06_CRTS_PRODUCTION.mp3
BACnet_en_2025-12-06_11LB_PROTOTYPE.mp3
```

### **Test Audio:**
```
test_{lang}_{date}_{scenario-topic}_{provider}_OS{sp}_MS{sp}_FS{sp}_{MODE}.mp3

Example:
test_de_2025-12-06_mvie-totr_CRTS_OS1.05_MS1.05_FS1.05_PROTOTYPE.mp3
```

**Provider Tags:**
- `CRTS` = Cartesia
- `11LB` = ElevenLabs

---

## ✅ **Installation Checklist**

- [ ] Python 3.8+ installed
- [ ] Code downloaded/cloned
- [ ] `pip install -r requirements.txt` completed
- [ ] ffmpeg installed and in PATH
- [ ] `config/.env` created with API keys
- [ ] Voice IDs configured in `podcast_config.json`
- [ ] `python podcast_pipeline.py` runs successfully
- [ ] Test audio generated

---

## 📞 **Support**

**Debug files:** `projects/{project}/debug/`  
**Verify API keys:** `cat config/.env`  
**Check voice IDs:** `cat config/podcast_config.json`  
**Test ffmpeg:** `ffmpeg -version`  
**Check dependencies:** `pip list | grep -E "anthropic|pydub|cartesia"`

---

## 🎉 **Quick Reference**

```bash
# Create podcast
python podcast_pipeline.py

# Adjust speeds
python tune_audio.py

# Translate script
python translate_script.py

# Update system
python smart_update.py

# Check dependencies
python smart_update.py  # Shows status at end
```

---

**All set! Happy podcasting!** 🎙️
