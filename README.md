# 🎙️ AI Podcast Pipeline

Two-person dialogue podcast generator with natural conversations, emotions, and interruptions.

**Use AI responsibly.**

---

## ⚡ Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure (see INSTALL_AND_SETUP.md)
cp config/.env.template config/.env
# Add your API keys

# 3. Run
python podcast_pipeline.py
```

**Full setup guide:** [INSTALL_AND_SETUP.md](INSTALL_AND_SETUP.md)

---

## 🎯 Features

### **Natural Dialogue**
- ✅ Emotions (`[excited]`, `[skeptical]`, `[laughs]`)
- ✅ Interruptions (`[overlapping]`, `[interrupting]`)
- ✅ Reactions (`[chuckles]`, `[sighs]`, `[gasps]`)
- ✅ 65+ emotion mappings for realistic variety

### **Two TTS Providers**
- **Cartesia** - Fast, affordable (~$0.05/min), 10ms crossfading eliminates clicks
- **ElevenLabs** - Premium voices, full emotion dynamics

### **Flexible Control**
- Per-voice speed settings (tune each speaker independently)
- Custom research contexts per project
- Document upload support (PDF, DOCX, PPTX)
- Multi-draft workflow with auto-versioning

### **Post-Processing Tools**
- `tune_audio.py` - Adjust speaker speeds post-generation
- `translate_script.py` - Translate to other languages
- `smart_update.py` - Safe system updates with backups

---

## 📊 Audio Quality

### **Recent Improvements**
- ✅ **Crossfading** - 10ms overlap eliminates clicks between segments
- ✅ **Emotion variety** - 65+ tags mapped across 5 base emotions
- ✅ **Duration accuracy** - Adjusted word count formula (222 wpm)
- ✅ **PCM processing** - Clean Cartesia audio without artifacts

---

## 🎛️ Primary Workflow

### **Standard Podcast Generation**

```bash
python podcast_pipeline.py
```

**Terminal prompts:**

```
1. Project name: BACnet
   └─> Creates: projects/BACnet/

2. Topic: BACnet protocol in building automation
   └─> Used for research & script generation

3. Duration (minutes): 15
   └─> Target length (actual: ±5% with 222 wpm formula)

4. Style:
   1. Dynamic, friendly science (Popular Scientific)
   2. In-depth technical analysis (Technical Deep Dive)
   3. Quick news update (News Brief)
   Choice: 1

5. Language:
   1. Deutsch (German)
   2. English
   3. Nederlands (Dutch)
   Choice: 1

6. Provider:
   1. ElevenLabs (Premium voices)
   2. Cartesia (Fast, affordable)
   Choice: 2

7. Mode:
   1. Prototype (standard quality, 64k bitrate)
   2. Production (high quality, full bitrate)
   Choice: 2

8. Speed (0.7-1.2, default 1.0): [Enter]
   └─> Optional: Override default speed
```

**Output:**
```
projects/BACnet/
├── scripts/BACnet_DE_2025-12-06_14-30_CRTS_draft1.txt
├── audio/BACnet_de_2025-12-06_CRTS_PRODUCTION.mp3
└── sources/BACnet_sources.txt
```

---

### **Test Mode Workflow**

**For quick voice testing (1-1.5 min outputs):**

```bash
python podcast_pipeline.py
```

**Special prompts when project = "test":**

```
1. Project name: test
   └─> Activates test mode

2. Scenario:
   1. Road trip argument
   2. Cooking disaster
   3. Movie scene analysis
   4. Random scenario
   Choice: 3

3. Topic: My Neighbor Totoro
   └─> Combined with scenario

4. Duration: 2 minutes
   └─> Always generates 1-1.5 min regardless

5-8. [Same as standard: Style, Language, Provider, Mode, Speed]
```

**Output:**
```
test_de_2025-12-06_mvie-totr_CRTS_OS1.00_MS1.00_FS1.00_PROTOTYPE.mp3
                    └─ scenario code (mvie-totr = movie + totoro)
                                     └─ speed settings encoded
```

**Use for:**
- Testing voices before full generation
- Experimenting with speeds
- Validating emotion tags
- Quick iteration cycles

---

## 🎛️ Per-Voice Speed Control

### **In Config** (Default speeds)
```json
{
  "providers": {
    "cartesia": {
      "voices": {
        "german": {
          "speaker_a_female": {
            "id": "voice-id-here",
            "default_speed": 0.97
          },
          "speaker_b_male": {
            "id": "voice-id-here",
            "default_speed": 1.0
          }
        }
      }
    }
  }
}
```

### **Post-Generation Tuning**
```bash
python tune_audio.py
# Select script
# Set individual speeds: Speaker A: 0.95, Speaker B: 1.05
# Regenerates audio with new speeds (no script changes)
```

**Use cases:**
- Balance volume between speakers (slower = quieter)
- Match pacing preferences
- Fix rushed/slow sections

---

## 🌍 Multi-Language Support

**Supported:** German, English, Dutch

**Translation workflow:**
```bash
# 1. Generate in German
python podcast_pipeline.py
# Topic: "BACnet protocol"
# Language: German

# 2. Translate script
python translate_script.py
# Select script → Choose English
# Preserves emotions & formatting

# 3. Generate English audio
python podcast_pipeline.py
# (Pipeline detects translated script, offers to reuse)
```

---

## 📁 Project Structure

```
myfirstpodcast/
├── config/
│   ├── .env                    # API keys (gitignored)
│   └── podcast_config.json     # Voice IDs, speeds, styles
├── templates/                   # Script templates (3 styles × 3 languages)
├── providers/                   # TTS provider implementations
│   ├── cartesia.py             # Cartesia with crossfading
│   └── elevenlabs.py           # ElevenLabs implementation
├── projects/                    # Your podcasts (gitignored)
│   └── {project}/
│       ├── audio/              # Generated MP3s
│       ├── scripts/            # Dialogue scripts
│       ├── sources/            # Your documents
│       └── debug/              # API payloads for troubleshooting
├── podcast_pipeline.py         # Main generator
├── tune_audio.py              # Post-processing: Speed adjustment
├── translate_script.py        # Script translation
└── smart_update.py            # Safe system updates
```

---

## 🎨 Podcast Styles

### **1. Popular Scientific** (Default)
- Dynamic, friendly science communication
- Natural dialogue with humor
- Target: 15 minutes
- Template: `popular_science_{language}_dynamic.txt`

### **2. Technical Deep Dive**
- In-depth technical analysis
- Expert-level discussion
- Target: 20 minutes
- Template: `technical_deep_dive_{language}.txt`

### **3. News Brief**
- Quick news update format
- Fast-paced, informative
- Target: 5 minutes
- Template: `news_brief_{language}.txt`

---

## 🔧 Configuration

### **API Keys** (`config/.env`)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
CARTESIA_API_KEY=...
```

### **Voice IDs** (`config/podcast_config.json`)
- 2 providers × 3 languages × 2 speakers = **12 voice IDs**
- Get from provider voice libraries
- Optional: Set per-voice default speeds

### **Research Contexts**
- **Global:** `templates/research_contexts/default.txt`
- **Project-specific:** `projects/{project}/sources/research_context.txt`

---

## 📈 Performance

**Generation Speed:**
- Research: 2-4 minutes
- Script: 3-5 minutes
- Audio (15 min podcast): 3-5 minutes
- **Total: ~10 minutes for 15-minute podcast**

---

## 🛠️ Tools Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| `podcast_pipeline.py` | Generate podcasts | Interactive prompts |
| `tune_audio.py` | Adjust speaker speeds | Post-generation tuning |
| `translate_script.py` | Translate scripts | Multi-language workflow |
| `smart_update.py` | Safe system updates | Backs up data, updates code |

---

## 📝 File Naming

**Scripts:**
```
{project}_{LANG}_{DATE}_{TIME}_{PROVIDER}_draft{N}.txt
Example: BACnet_DE_2025-12-06_14-30_CRTS_draft1.txt
```

**Audio:**
```
{project}_{lang}_{date}_{provider}_{MODE}.mp3
Example: BACnet_de_2025-12-06_CRTS_PRODUCTION.mp3
```

**Test Audio:**
```
test_{lang}_{date}_{scenario-topic}_{provider}_OS{sp}_MS{sp}_FS{sp}_{MODE}.mp3
Example: test_de_2025-12-06_mvie-totr_CRTS_OS1.00_MS1.00_FS1.00_PROTOTYPE.mp3
```

**Provider tags:** `CRTS` (Cartesia), `11LB` (ElevenLabs)

---

## 🔄 Updates

```bash
# Automatic (recommended)
python smart_update.py

# Manual
cp {file}_FIXED.py {destination}
pip install -r requirements.txt
```

**smart_update.py features:**
- ✅ Backs up all data (.env, configs, projects)
- ✅ Updates only core files
- ✅ Checks dependencies (Python + ffmpeg)
- ✅ Cleans up temporary files
- ✅ Shows status report

---

## 📚 Documentation

- **[INSTALL_AND_SETUP.md](INSTALL_AND_SETUP.md)** - Complete setup guide

---

## 📄 License

**CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International)

**You are free to:**
- ✅ Share - Copy and redistribute
- ✅ Adapt - Remix, transform, and build upon

**Under these terms:**
- 📌 **Attribution** - You must give appropriate credit, provide a link to the license, and indicate if changes were made
- 🚫 **NonCommercial** - You may not use the material for commercial purposes
- 🔄 **ShareAlike** - If you remix, transform, or build upon the material, you must distribute your contributions under the same license

**Full license:** https://creativecommons.org/licenses/by-nc-sa/4.0/

---

## 🙏 Acknowledgments

- **Anthropic Claude** - Script generation & research
- **Cartesia** - Fast, high-quality TTS
- **ElevenLabs** - Premium voice synthesis

---

**Generate natural, engaging podcasts in minutes!** 🎙️
