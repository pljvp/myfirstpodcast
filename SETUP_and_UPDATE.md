# Setup & Update

## First Time Setup (5 min)

```bash
# Clone from GitHub
git clone https://github.com/yourusername/podcast-pipeline.git
cd podcast-pipeline

# Make scripts executable
chmod +x smart_update.sh translate_script.py tune_audio.py

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API keys
cp config/.env.example config/.env
nano config/.env
# Add:
#   ANTHROPIC_API_KEY=your_key_here
#   ELEVENLABS_API_KEY=your_key_here

# Optional: Customize voices
nano config/podcast_config.json

# Run
python podcast_pipeline.py
```

## New Features

### Source Documents Integration
Add your own documents to the research process:
- Supported: PDF, Word (.docx), PowerPoint (.pptx), Text (.txt, .md)
- Location: `projects/{project}/sources/`
- Used alongside web research automatically

### Post-Processing Tools

**Translate existing scripts:**
```bash
python translate_script.py
# Convert German → English → Dutch
# Preserves audio tags and formatting
```

**Adjust audio speeds:**
```bash
python tune_audio.py
# Fine-tune Speaker A/B speeds (0.7-1.2)
# Regenerate audio without re-running Claude
```

See [NEW_FEATURES.md](NEW_FEATURES.md) for detailed usage guide.

## Easy Updating (30 sec)

Smart updating allows you to take in many files at once, from any LLM output or manual edits.

```bash
cd podcast-pipeline

# Place new files (any naming convention works)
# - podcast_pipeline_FIXED.py or podcast_pipeline_new.py
# - template_FIXED.txt files
# - new template files

# Run smart update
./smart_update.sh
```

The script automatically:
- Detects new pipeline files
- Renames _FIXED to correct names
- Moves templates to correct folders
- Backs up your configs
- Restores all your settings
- Preserves project contexts

All configs, API keys, templates, and project contexts preserved automatically.

Done.
