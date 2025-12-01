# AI Podcast Pipeline

Generate professional podcasts with Claude research + multi-provider TTS audio.

## Features

- **Multi-Provider TTS:** ElevenLabs or Cartesia (Sonic)
- **Claude AI Research:** Web search + your documents
- **Multi-Language:** German, English, Dutch
- **Smart Script Detection:** Reuse existing scripts
- **Source Documents:** PDFs, Word, PowerPoint integration
- **Post-Processing Tools:** Translation, speed tuning

## File Structure

```
myfirstpodcast/
├── podcast_pipeline.py          # Main script
├── tune_audio.py                 # Adjust speaker speeds
├── translate_script.py           # Translate to other languages
├── smart_update.sh               # Update automation (chmod +x)
├── requirements.txt              # Dependencies
├── config/
│   ├── .env                      # API keys (YOU create)
│   └── podcast_config.json       # Providers, voices, styles, languages
├── providers/                    # TTS provider modules
│   ├── __init__.py
│   ├── base.py                   # Base provider class
│   ├── elevenlabs.py             # ElevenLabs implementation
│   └── cartesia.py               # Cartesia Sonic implementation
├── templates/
│   ├── popular_science_{language}_dynamic.txt
│   ├── technical_deep_dive_{language}.txt
│   ├── news_brief_{language}.txt
│   └── research_contexts/
│       └── default.txt           # Reusable research template
└── projects/                     # Created by script
    └── {project_name}/
        ├── prompts/              # Prompt versions
        ├── sources/
        │   ├── research_context.txt   # Project-specific research instructions
        │   └── sources_list.txt       # Extracted sources from Claude
        ├── scripts/
        │   ├── {project}_{LANG}_{DATE}_{PROVIDER}_draft{N}.txt
        │   └── {project}_sources.txt  # Research sources (not in audio)
        ├── audio/
        │   └── {project}_{LANG}_{DATE}_{PROVIDER}_{MODE}.mp3
        └── debug/
            └── chunk_{N}_{PROVIDER}_content.json
```

## Provider System

### **ElevenLabs (11LB)**
- Full emotion dynamics
- Natural interruptions
- Quality tiers: Prototype (64kbps) / Production (128kbps+)
- Speed range: 0.7-1.2

### **Cartesia (CRTS)**
- Sonic model
- Faster generation
- Emotion-optimized
- Always full quality (44100 Hz)
- Speed range: 0.7-1.2 (auto-converted to Cartesia's -1.0 to 1.0)

### **Speed Settings (Unified Interface)**
- **User input:** Always use ElevenLabs-style range (0.7-1.2)
- **ElevenLabs:** Uses value directly
- **Cartesia:** Auto-converts internally using formula: `(speed - 1.0) * 2.0`
- **Speed tags in test audio:** Always show ElevenLabs-style value (e.g., `OS1.05`)
- **Result:** Same speed input produces comparable audio across both providers

### **Test Mode Audio Speed Tags**
Test audio filenames include speed settings for easy comparison:
```
test_de_2025-12-01_mvie-totr_CRTS_OS1.05_MS1.05_FS1.05_PROTOTYPE.mp3
                                      ^^^^^^ ^^^^^^ ^^^^^^
                                      Overall Male  Female
```
- **OS** (Overall Speed): Base speed setting (0.7-1.2)
- **MS** (Male Speed): Speaker B actual speed (includes per-voice adjustments)
- **FS** (Female Speed): Speaker A actual speed (includes per-voice adjustments)

Note: Speed tags always show ElevenLabs-style values for consistency, even for Cartesia audio.

### **File Naming with Provider Tags**

**Scripts:**
```
{project}_{LANG}_{DATE}_{TIME}_{PROVIDER}_draft{N}.txt

Examples:
BACnet_DE_2025-11-29_15-13_CRTS_draft1.txt  (Cartesia)
BACnet_DE_2025-11-29_15-13_11LB_draft1.txt  (ElevenLabs)
```

**Audio:**
```
{project}_{LANG}_{DATE}_{TIME}_{PROVIDER}_{MODE}.mp3

Examples:
BACnet_DE_2025-11-29_15-30_CRTS_PROTOTYPE.mp3
BACnet_DE_2025-11-29_15-30_11LB_PRODUCTION.mp3
```

**Debug:**
```
chunk_{N}_{PROVIDER}_content.json

Examples:
chunk_1_CRTS_content.json
chunk_1_11LB_content.json
```

## User Flow

### **1. Run:** 
```bash
python podcast_pipeline.py
```

### **2. Project Setup:**
- **Project name:** Folder/file names (preserves case: BACnet stays BACnet)
  - Special: `test` triggers test mode (voice tuning with short scenarios)
- **Podcast topic:** Content description (allows spaces)
- **Duration:** Minutes (auto-calculates word count at 180 words/min for dialogue)

### **3. Style Selection:**
```
1. Dynamic, friendly science communication (v3 - natural dialogue)
2. In-depth technical analysis for experts
3. Quick news update format
```

### **4. Language Selection:**
```
1. Deutsch (German) - DE
2. English - EN
3. Nederlands (Dutch) - NL
```

### **5. TTS Provider Selection:**
```
============================================================
TTS PROVIDER SELECTION
============================================================

Select TTS provider
    1. ElevenLabs (full emotion dynamics, interruptions)
    2. Cartesia (faster generation, emotion-optimized)
Choice: 2
	  Scripts will be tagged with: CRTS
	  Cartesia Note: Always generates full quality
	                 (API does not support prototype/production tiers)

Select mode
    1. Prototype (lower quality, reduced cost for testing)
    2. Production (full quality)
Choice: 1

Speech speed (0.7-1.2, default 1.05, Enter to use default): 
Using default speed: 1.05
```

### **6. Script Detection (NEW!):**

If existing scripts found:
```
⚠️  Found 3 existing script(s) with CRTS tag:
    Latest: BACnet_DE_2025-11-29_15-13_CRTS_draft3.txt (2025-11-29 15:13)

    1. Use existing script (skip to audio generation)
    2. Generate new script (continue with research/prompt setup)
    3. Cancel
Choice: 1

[INFO] Loading: BACnet_DE_2025-11-29_15-13_CRTS_draft3.txt
[INFO] Skipping to audio generation...
```

**Benefits:**
- Skip research/prompt if script already exists
- Quick audio regeneration with different providers/modes
- Provider-specific detection (only shows CRTS scripts if you selected Cartesia)

### **7. Research Context (if generating new):**
```
1. Use as-is (proceed with current context)
2. Edit current context (customize for this project)
3. Reset to default template
4. Show current context
```

### **8. Prompt Template (if generating new):**
```
1. Use default template (style / language)
2. Load existing template from project
3. Copy template from templates folder
4. Edit the chosen template before generating
5. Start with blank prompt
```

### **9. Source Documents (if generating new):**
```
============================================================
SOURCE DOCUMENTS CHECK
============================================================
Found 1 document(s) in sources folder:
  - BACnet_overview.pdf

Options:
  1. Proceed (use existing documents if any)
  2. List current documents
  3. Add new source files

Choice: 1
```

**Supported formats:**
- Text: `.txt`, `.md`
- Documents: `.docx`
- PDF: `.pdf`
- Presentations: `.pptx`

### **10. Claude Generation:**
```
============================================================
CLAUDE IS WORKING...
============================================================
- Conducting online research
- Analyzing sources
- Generating podcast script
- Formatting dialogue

This may take 30-60 seconds...
============================================================

✓ Script generated successfully!

[USAGE] Claude - Input: 3704 tokens, Output: 5605 tokens
✓ Sources extracted and saved to: projects/BACnet/sources/sources_list.txt
Script generated! (2167 words)
Saved to: projects/BACnet/scripts/BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt
```

### **11. Script Review:**
```
============================================================
SCRIPT REVIEW
============================================================
Script location: projects/BACnet/scripts/BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt
============================================================

What would you like to do?
    1. Open script in text editor to review
    2. Approve script and proceed to audio
    3. Ask Claude to revise (provide guidance)
    4. Edit script file manually, then regenerate from edits
    5. Save prompt variant to project
    6. Cancel
```

### **12. Audio Generation:**
```
============================================================
AUDIO GENERATION - PROTOTYPE MODE
============================================================

Proceed with audio generation? (Y/n): y

[INFO] Cleaning script for audio generation...
[INFO] ✓ CUT SOURCES: Removed 1605 chars after 'SOURCES FOUND:'
[INFO] ✓ Verified clean - no sources in cleaned script

============================================================
TTS PROVIDER: CARTESIA
Model: sonic-english
Speed: 1.05 (ElevenLabs) → 0.10 (Cartesia)
============================================================

[Segment 1/145] 140 chars ['positivity:high']
[Segment 2/145] 98 chars ['curiosity:high']
...
✓ Audio generated (15.2 MB)

✓ Audio saved: projects/BACnet/audio/BACnet_DE_2025-11-29_19-25_CRTS_PROTOTYPE.mp3
[USAGE] CARTESIA - 10358 characters processed
```

## Post-Processing Tools

### **translate_script.py**

Translate existing scripts to another language:

```bash
python translate_script.py

Available projects:
  1. BACnet
  2. protocols
Select project (1-2): 1

Available scripts in 'BACnet':
  1. BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt (2025-11-29 19:23)
Select script (1-1): 1

Loaded: BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt
Detected source language: DE
Detected provider: CARTESIA (from filename)
[INFO] Translation will preserve CARTESIA format

Available languages:
  1. Deutsch (German) - DE
  2. English - EN
  3. Nederlands (Dutch) - NL
Select target language (1-3): 2

[INFO] Calling Claude API for translation...
✓ Translation complete!

Translated script saved to:
  projects/BACnet/scripts/BACnet_EN_2025-11-29_19-30_CRTS_draft1.txt
```

**Features:**
- Preserves audio tags `[excited]`, `[curious]`, etc.
- Maintains `Speaker A:` / `Speaker B:` format
- Preserves provider tag (CRTS or 11LB)
- Optional audio generation after translation

---

### **tune_audio.py**

Regenerate audio with custom speaker speeds:

```bash
python tune_audio.py

Available projects:
  1. BACnet
Select project (1-1): 1

Available scripts in 'BACnet':
  1. BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt (2025-11-29 19:23)
Select script (1-1): 1

Loaded: BACnet_DE_2025-11-29_19-23_CRTS_draft1.txt (10358 chars)
Detected language: DE
Detected provider: CARTESIA (from filename)
[INFO] Audio will be generated using CARTESIA

Current default speed: 1.05
Speed range: 0.7 (slow) to 1.2 (fast)

Speaker A speed (default 1.05): 1.1
Speaker B speed (default 1.05): 1.0

[INFO] Using custom speeds: Speaker A = 1.1, Speaker B = 1.0
[INFO] Provider: CARTESIA

✓ Audio generated (14.8 MB)
✓ Audio saved to: projects/BACnet/audio/BACnet_DE_2025-11-29_19-35_A1.1_B1.0_CRTS_TUNED.mp3
```

**Features:**
- Auto-detects provider from filename
- Per-speaker speed control (experimental)
- Uses correct provider API
- Speed conversion for Cartesia (0.7-1.2 → -1.0 to 1.0)

## Configuration

### **config/.env**

Create this file with your API keys:

```bash
# Required for script generation
ANTHROPIC_API_KEY=sk-ant-...

# TTS Providers (at least one required)
ELEVENLABS_API_KEY=sk_...
CARTESIA_API_KEY=...
```

### **config/podcast_config.json**

Provider configuration structure:

```json
{
  "providers": {
    "elevenlabs": {
      "api_key_env": "ELEVENLABS_API_KEY",
      "voices": {
        "german": {
          "speaker_a_female": "voice_id_here",
          "speaker_b_male": "voice_id_here"
        },
        "english": { ... },
        "dutch": { ... }
      }
    },
    "cartesia": {
      "api_key_env": "CARTESIA_API_KEY",
      "voices": {
        "german": {
          "speaker_a_female": "voice_id_here",
          "speaker_b_male": "voice_id_here"
        },
        "english": { ... },
        "dutch": { ... }
      }
    }
  },
  "styles": {
    "popular_scientific": {
      "description": "Dynamic, friendly science communication (v3 - natural dialogue)",
      "default_template_file": "templates/popular_science_{language}_dynamic.txt"
    },
    "technical_deep_dive": { ... },
    "news_brief": { ... }
  },
  "languages": {
    "german": {
      "name": "Deutsch (German)",
      "speed": 1.05
    },
    "english": { ... },
    "dutch": { ... }
  },
  "elevenlabs_settings": {
    "prototype": {
      "quality": "standard",
      "downsample_enabled": true,
      "downsample_bitrate": "64k"
    },
    "production": {
      "quality": "high",
      "downsample_enabled": false
    }
  }
}
```

## Audio Tags

Use these in scripts for emotional delivery:

```
Speaker A: [excited] This is amazing!
Speaker B: [curious] Really? Tell me more.
Speaker A: [laughs] Well, here's the thing...
Speaker B: [thoughtful] I see what you mean.
```

**Common tags:**
- `[excited]` `[enthusiastic]` `[happy]` → Positivity
- `[curious]` `[questioning]` `[analytical]` → Curiosity
- `[surprised]` `[amazed]` → Surprise
- `[laughs]` `[chuckles]` → Laughter
- `[thoughtful]` `[concerned]` → Reflection

## Templates

### **Popular Science** (15 min)
- Dynamic, friendly dialogue
- Natural interruptions
- Audience: General public
- Tags: `[excited]`, `[curious]`, `[laughs]`

### **Technical Deep Dive** (20 min)
- Expert-level analysis
- Peer-to-peer discussion
- Audience: Professionals
- Tags: `[analytical]`, `[thoughtful]`, `[questioning]`

### **News Brief** (5 min)
- Fast-paced updates
- Breaking news energy
- Audience: Quick info seekers
- Tags: `[energetic]`, `[urgently]`, `[dramatically]`

Each available in: German, English, Dutch

## Troubleshooting

### **Speed Issues**
- **ElevenLabs:** Range 0.7-1.2 used directly
- **Cartesia:** Range 0.7-1.2 auto-converted to -1.0 to 1.0
- Check debug files: `projects/{project}/debug/chunk_*_CRTS_content.json`

### **Provider Errors**
- **Wrong provider used:** Check script filename has correct tag (CRTS or 11LB)
- **API key missing:** Verify `.env` has correct key name
- **Emotion format:** Cartesia uses arrays `["positivity:high"]`, not strings

### **Case Sensitivity**
- Project names preserve case: `BACnet` stays `BACnet`
- All scripts use exact project folder name

### **Script Detection**
- Only shows scripts matching selected provider
- Checks filename pattern: `{project}_{LANG}_*_{PROVIDER}_draft*.txt`
- Case-sensitive project name matching

## Updates

Use `smart_update.sh` to apply updates:

```bash
chmod +x smart_update.sh
./smart_update.sh
```

**Preserves:**
- All config files (`.env`, `podcast_config.json`)
- All projects and generated content
- Custom templates
- Research contexts

**Updates:**
- Main pipeline script
- Provider modules
- Utility scripts (tune_audio, translate_script)
- Template improvements

## Requirements

```bash
pip install anthropic requests python-dotenv python-docx PyPDF2 python-pptx
```

See `requirements.txt` for versions.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   cd config
   nano .env
   # Add your API keys
   ```

3. **Configure voices in `podcast_config.json`**

4. **Run pipeline:**
   ```bash
   python podcast_pipeline.py
   ```

5. **Follow prompts** for project setup, provider selection, and generation

## Test Mode (Voice Tuning)

**Purpose:** Quick 1-1.5 minute test samples for voice/emotion tuning without expensive 25-minute full podcasts.

**Trigger:** Project name = `test` (case-insensitive)

**Features:**
- **Fast workflow:** Skips research context and template menus
- **Predefined scenarios:** Road trips, cooking disasters, movie analysis, or random
- **Speed tags:** Filenames include OS/MS/FS speed settings
- **Scenario tags:** Easy identification (`mvie-totr`, `cook-pizz`, etc.)

**Example workflow:**
```bash
python podcast_pipeline.py

Enter project name: test

[TEST MODE ACTIVATED]

Select test scenario type:
    1. Road trip argument
    2. Cooking disaster  
    3. Movie scene analysis
    4. Random scenario
Choice: 3

Movie scene analysis scenarios:
    1. Pulp Fiction (briefcase scene)
    2. The Matrix (red pill/blue pill)
    3. Star Trek (Borg: resistance is futile)
    4. Totoro (Catbus scene)
    5. Inception (dream layers)
    6. Random
Choice: 4

[TEST MODE] Skipping research context
[TEST MODE] Loading test template...
Using template: templates/popular_science_german_TEST.txt

✓ Script saved: test_DE_2025-12-01_mvie-totr_CRTS_draft1.txt
✓ Audio saved: test_de_2025-12-01_mvie-totr_CRTS_OS1.05_MS1.05_FS1.05_PROTOTYPE.mp3
```

**File naming:**
```
Scripts: test_DE_2025-12-01_22-30_mvie-totr_CRTS_draft1.txt
Audio:   test_de_2025-12-01_mvie-totr_CRTS_OS1.05_MS1.05_FS1.05_PROTOTYPE.mp3
```

**Benefits:**
- Test voice settings in < 2 minutes
- Compare speeds side-by-side
- Fine-tune emotions before full production
- Cost-effective iteration

## Advanced Features

### **Research Contexts**
- Global default: `templates/research_contexts/default.txt`
- Project-specific: `projects/{project}/sources/research_context.txt`
- Customize research instructions per project

### **Source Documents**
- Add PDFs, Word docs, PowerPoints to `projects/{project}/sources/`
- Claude analyzes them alongside web research
- Automatic text extraction

### **Debug Mode**
- Always enabled with verbose logging
- Chunk-by-chunk content saved
- Error details in debug JSON files
- Check `projects/{project}/debug/` for troubleshooting

### **Multi-Draft Workflow**
- Each revision saves as new draft
- Filename: `{project}_{LANG}_{DATE}_{PROVIDER}_draft{N}.txt`
- Full revision history maintained
- Easy rollback to previous versions

## License

MIT

## Support

For issues, check:
1. Debug JSON files in `projects/{project}/debug/`
2. Error messages in terminal
3. Provider-specific documentation
4. API key configuration in `.env`

---

**Version:** 3.0  
**Last Updated:** 2025-11-29  
**Providers:** ElevenLabs, Cartesia Sonic  
**Languages:** German, English, Dutch
