# Setup & Update

## First Time Setup (5 min)

```bash
# Extract
tar -xzf myfirstpodcast_v3.tar.gz
cd myfirstpodcast_v3

# Make scripts executable
chmod +x smart_update.sh

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API keys
cp config/.env.template config/.env
nano config/.env
# Add:
#   ANTHROPIC_API_KEY=your_key_here
#   ELEVENLABS_API_KEY=your_key_here

# Configure voices (optional - defaults provided)
nano config/podcast_config.json
# Update voice IDs for DE/EN/NL if needed

# Create default research template
mkdir -p templates/research_contexts
nano templates/research_contexts/default.txt
# Create your reusable research template

# Run
python podcast_pipeline.py
```

## Updates (30 sec)

```bash
cd myfirstpodcast_v3

# Place new files
cp new_podcast_pipeline.py podcast_pipeline_new.py
cp new_template.txt templates/

# Run update (backs up & restores everything)
./smart_update.sh
```

All configs, templates, and project contexts preserved automatically.

Done.
