AA# 🎙️ AI Podcast Pipeline

Two-person dialogue podcast generator with natural conversations and emotions.

**Use AI responsibly.**

---

## ⚡ Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp config/.env.template config/.env
# Add your API keys

# 3. Run
python podcast_pipeline.py
```

---

## 🎯 Features

### **Natural Dialogue**
- ✅ Provider-specific emotion tags (auto-selected per provider)
- ✅ Reactions (`[laughs]`, `[sighs]`, `[gasps]`)
- ✅ 60+ Cartesia native emotions, full ElevenLabs dynamics

### **Two TTS Providers**
- **Cartesia** - Fast, affordable (~$0.05/min), native emotion support
- **ElevenLabs** - Premium voices, interruptions & overlapping speech

### **Scalable Architecture**
- Provider config files (`providers/configs/*.yaml`)
- Template placeholders for easy 3rd provider addition
- Per-voice speed settings

### **Post-Processing Tools**
- `tune_audio.py` - Adjust speaker speeds post-generation
- `translate_script.py` - Translate to other languages

---

## 🎛️ Primary Workflow

```bash
python podcast_pipeline.py
```

**Prompts:** Project name → Topic → Duration → Style → Language → Provider → Mode

**Output:**
```
projects/myprojectname/
├── scripts/myprojectname_DE_2025-12-06_14-30_CRTS_draft1.txt
├── audio/myprojectname_de_2025-12-06_CRTS_PRODUCTION.mp3
└── sources/myprojectname_sources.txt
```

---

## 📁 Project Structure

```
myfirstpodcast/
├── config/
│   ├── .env                    # API keys (gitignored)
│   └── podcast_config.json     # Voice IDs, speeds, styles
├── templates/                   # Script templates (3 styles × 3 languages)
├── providers/
│   ├── configs/                # Provider-specific emotion configs
│   │   ├── cartesia.yaml
│   │   └── elevenlabs.yaml
│   ├── cartesia.py
│   └── elevenlabs.py
├── projects/                    # Your podcasts (gitignored)
├── podcast_pipeline.py         # Main generator
├── tune_audio.py              # Speed adjustment
└── translate_script.py        # Script translation
```

---

## 🔧 Configuration

### **API Keys** (`config/.env`)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
CARTESIA_API_KEY=...
```

### **Voice IDs** (`config/podcast_config.json`)
- 2 providers × 3 languages × 2 speakers = 12 voice IDs
- Optional: Set per-voice default speeds

---

## 🛠️ Tools Reference

| Tool | Purpose |
|------|---------|
| `podcast_pipeline.py` | Generate podcasts |
| `tune_audio.py` | Adjust speaker speeds |
| `translate_script.py` | Translate scripts |
| `smart_update.py` | Safe updates with backups |

---

## 📄 License

**CC BY-NC-SA 4.0** - Attribution, NonCommercial, ShareAlike

---

**Generate natural, engaging podcasts in minutes!** 🎙️
