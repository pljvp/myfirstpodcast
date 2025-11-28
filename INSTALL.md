# Install

## From GitHub

```bash
# Clone repository
git clone https://github.com/yourusername/podcast-pipeline.git
cd podcast-pipeline

# Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API keys
cp config/.env.example config/.env
nano config/.env
# Add your keys:
#   ANTHROPIC_API_KEY=your_key_here
#   ELEVENLABS_API_KEY=your_key_here

# Optional: Customize voice IDs
nano config/podcast_config.json

# Make scripts executable
chmod +x smart_update.sh translate_script.py tune_audio.py

# Run
python podcast_pipeline.py
```

## Dependencies

**Core:**
- `anthropic` - Claude API
- `requests` - ElevenLabs API
- `python-dotenv` - Environment variables

**Document Reading (optional):**
- `python-docx` - Word documents
- `PyPDF2` - PDF files
- `python-pptx` - PowerPoint presentations

If document libraries are missing, pipeline will show install instructions and skip unsupported formats.

## Structure

```
podcast-pipeline/
├── podcast_pipeline.py       # Main script
├── translate_script.py       # Translate existing scripts (NEW)
├── tune_audio.py             # Adjust audio speeds (NEW)
├── smart_update.sh           # Update tool
├── requirements.txt          # Dependencies
├── config/
│   ├── .env.example          # API key template
│   └── podcast_config.json   # Voice IDs, languages
├── templates/
│   ├── popular_science_*.txt
│   ├── technical_deep_dive_*.txt
│   └── news_brief_*.txt
└── projects/                 # Auto-created
    └── {project}/
        ├── sources/          # Add your documents here (NEW)
        ├── scripts/
        └── audio/
```

## First Run

The script will guide you through:
1. Project name
2. Podcast topic
3. Duration
4. Style (popular science / technical / news)
5. Language (DE / EN / NL)
6. Mode (prototype / production)
7. **Source documents** (add PDFs/Word/PowerPoint - optional)

Audio saved to: `projects/{project}/audio/{project}_{topic}_{lang}_{date}_{MODE}.mp3`

## New Features

### Add Your Own Documents
```bash
# During podcast creation, at SOURCE DOCUMENTS CHECK:
# Copy files to: projects/{project}/sources/
# Supported: .txt .md .docx .pdf .pptx
```

### Translate Scripts
```bash
python translate_script.py
# Convert German → English → Dutch
```

### Adjust Audio Speeds
```bash
python tune_audio.py
# Fine-tune Speaker A/B speeds independently
```

See [NEW_FEATURES.md](NEW_FEATURES.md) for detailed usage.

Done.
