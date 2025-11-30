# Cartesia TTS Integration - Complete Installation Guide

## 🎯 What This Update Does

**MAJOR REFACTOR** - Provider-optimized script generation

### Key Changes:
1. ✅ **Provider selection BEFORE script generation**
2. ✅ **Provider-specific emotion tags** (ElevenLabs full dynamics vs Cartesia optimized)
3. ✅ **Filenames include provider** (project_DE_2025-11-29_11LB_draft1.txt)
4. ✅ **tune_audio.py & translate_script.py auto-detect provider**
5. ✅ **No emotion quality loss** - each provider gets optimal tags

---

## 📦 What's Included

```
myfirstpodcast_cartesia_20251129.zip
├── providers/                          ← NEW FOLDER
│   ├── __init__.py
│   ├── base.py                         (Abstract base)
│   ├── elevenlabs.py                   (Full dynamics + interruptions)
│   └── cartesia.py                     (Emotion-optimized)
├── podcast_pipeline_UPDATED.py         (Provider selection workflow)
├── podcast_config_UPDATED.json         (Provider configs)
├── requirements_UPDATED.txt            (+ cartesia)
│   ├── _env_UPDATED.template           (+ CARTESIA_API_KEY)
├── smart_update.sh                     (NO version suffix!)
├── tune_audio_UPDATED.py               (Provider auto-detect)
├── translate_script_UPDATED.py         (Provider preservation)
└── INSTALL.md                          (This file)
```

---

## ⚡ Installation (5 minutes)

### Step 1: Extract

```bash
cd ~/Downloads
unzip myfirstpodcast_cartesia_20251129.zip
cd myfirstpodcast_cartesia_20251129
```

### Step 2: Copy to Project

```bash
cp -r * /path/to/myfirstpodcast/
cd /path/to/myfirstpodcast
```

### Step 3: Run Smart Update

```bash
./smart_update.sh
```

**It will:**
- Backup everything (`.backup/` + timestamped folder)
- Install `providers/` folder
- Update pipeline, tune_audio, translate_script
- Ask about config replacement (say **Y**)
- Preserve API keys, templates, projects

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

**New:** `cartesia==1.1.0`

### Step 5: Add Cartesia API Key

```bash
nano config/.env
```

Add:
```
CARTESIA_API_KEY=your_cartesia_key_here
```

### Step 6: Configure Cartesia Voices

```bash
nano config/podcast_config.json
```

Find `"cartesia"` section, replace placeholders:

```json
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
```

Get voice IDs: https://cartesia.ai/voices

---

## 🎯 New Workflow

### Creating a Podcast

```
1. Project setup (name, topic, duration)
2. Style selection
3. Language selection

4. [NEW] TTS PROVIDER SELECTION ← Choose here!
   "Select TTS Provider:"
   "  1. ElevenLabs (full emotion dynamics, interruptions)"
   "  2. Cartesia (faster, emotion-optimized)"
   
   Provider (1-2, default=1): 2
   
   [INFO] Selected: CARTESIA
   [INFO] Template optimized for Cartesia
   [INFO] Scripts will be tagged with: CRTS

5. Mode (Prototype/Production)
6. Speed setting
7. Template selection
8. Script generation (optimized for chosen provider)

Script saved: project_DE_2025-11-29_CRTS_draft1.txt
                                      ^^^^
                                      Provider tag!
```

### Audio Filenames

```
project_DE_2025-11-29_14-30_11LB_PROTOTYPE.mp3    ← ElevenLabs
project_DE_2025-11-29_14-35_CRTS_PRODUCTION.mp3   ← Cartesia
```

---

## 🔄 Provider-Specific Features

### ElevenLabs Scripts

**Template includes:**
```
[interrupting] [overlapping] [interjecting]
[fast-paced] [slowly] [pause]
[nervous][hesitant] - Stacked tags
```

**Example:**
```
Speaker A: [excited] [fast-paced] This is incredible!
Speaker B: [interrupting] [curious] Wait, what about—
Speaker A: [overlapping] [laughs] Exactly!
```

**Best for:** Maximum dialogue dynamics, natural interruptions

---

### Cartesia Scripts

**Template includes:**
```
[excited] [curious] [skeptical] [surprised]
[thoughtful] [confused] [amused] [impressed]
[laughs] [sighs] [gasps]

Interruptions via em dashes:
Speaker A: The implications are—
Speaker B: Are they really that significant?
```

**Example:**
```
Speaker A: [excited] You won't believe this.
Speaker B: [curious] Tell me!
Speaker A: [thoughtful] So researchers discovered—
Speaker B: [skeptical] Sounds too good to be true.
Speaker A: [laughs] I know, right?
```

**Best for:** Faster generation, emotion-focused delivery, privacy

---

## 🛠️ tune_audio.py & translate_script.py

**Auto-detect provider from filename:**

```bash
./tune_audio.py

Available scripts:
  1. project_DE_2025-11-29_CRTS_draft1.txt

Select script: 1

[INFO] Detected provider: Cartesia (from filename)
[INFO] Audio will use Cartesia

...generates with Cartesia automatically
```

**Translate preserves provider:**
```
Original:    project_DE_2025-11-29_11LB_draft1.txt
Translated:  project_NL_2025-11-29_11LB_draft1.txt
                                     ^^^^ Preserved!
```

---

## ✅ Verification

After installation:

```bash
# Check providers folder
ls -la providers/
# Should show: __init__.py, base.py, elevenlabs.py, cartesia.py

# Check cartesia installed
pip list | grep cartesia
# Should show: cartesia 1.1.0

# Test ElevenLabs (ensure nothing broke)
python podcast_pipeline.py
# Select ElevenLabs, generate test podcast

# Test Cartesia
python podcast_pipeline.py
# Select Cartesia, generate test podcast
```

---

## 🔍 File Naming Convention

```
{project}_{LANG}_{DATE}_{PROVIDER}_{draft}.txt

Examples:
strategies_DE_2025-11-29_11LB_draft1.txt   ← ElevenLabs script
strategies_DE_2025-11-29_CRTS_draft1.txt   ← Cartesia script
strategies_NL_2025-11-29_11LB_draft1.txt   ← Translated (preserved)

Audio:
strategies_DE_2025-11-29_14-30_11LB_PROTOTYPE.mp3
strategies_DE_2025-11-29_14-35_CRTS_PRODUCTION.mp3
```

**Provider Tags:**
- `11LB` = ElevenLabs
- `CRTS` = Cartesia

---

## 📊 Comparison

| Feature | ElevenLabs | Cartesia |
|---------|------------|----------|
| **Emotion Tags** | Full set | Optimized subset |
| **Interruptions** | `[interrupting]` tags | Em dashes (—) |
| **Dynamics** | `[fast-paced]` etc | Via emotion intensity |
| **Generation** | ~5-10s/chunk | ~2-5s/segment |
| **Cost** | $5-330/mo | ~$0.05/min |
| **Privacy** | Server processed | No retention |
| **Best For** | Max dynamics | Speed + emotions |

---

## 🛠️ Troubleshooting

### "Module 'providers' not found"
```bash
ls -la providers/
# If missing: extract again and copy
```

### "Unknown provider 'cartesia'"
```bash
# Check config structure
cat config/podcast_config.json | head -20
# Should see "providers" section
```

### Cartesia voice ID errors
```bash
# Edit config, replace ALL placeholders
nano config/podcast_config.json
# Search for: REPLACE_WITH_YOUR_CARTESIA_VOICE_ID
```

### Scripts use wrong provider
- Provider is chosen BEFORE script generation
- Check filename for provider tag (_11LB_ or _CRTS_)
- tune/translate auto-detect from filename

---

## 🔮 Future: Adding More Providers

Architecture is ready! To add Resemble:

1. Create `providers/resemble.py` (copy cartesia structure)
2. Add provider selection option
3. Add config block
4. Done - ~30 minutes

---

## ✅ What Works

- ✅ Both providers fully functional
- ✅ Provider-specific emotion optimization
- ✅ Auto-detection in tune/translate
- ✅ All languages (German, English, Dutch)
- ✅ All templates (popular science, technical, news)
- ✅ Speed control both providers
- ✅ Prototype/Production modes

---

## 📝 Notes

- **Choose provider FIRST** - before script generation
- **Scripts optimized** - different tags per provider
- **Auto-preservation** - tune/translate keep provider
- **No data loss** - smart_update backs up everything
- **Easy rollback** - old files in `.backup/`

---

Done! Test with both providers. 🎸
