# Install v3.1

```bash
cd myfirstpodcast_v3

# Copy files (remove _FIXED suffix)
cp podcast_pipeline_FIXED.py podcast_pipeline.py
cp podcast_config.json config/

# Dutch templates
cp popular_science_dutch_dynamic.txt templates/
cp news_brief_dutch.txt templates/
cp technical_deep_dive_dutch.txt templates/

# Make executable
chmod +x smart_update.sh podcast_pipeline.py

# Done
python podcast_pipeline.py
```

## Changes

1. **Sources removed** - Everything after "SOURCES FOUND:" cut before audio
2. **Speed control** - Default 1.05, prompt for 0.7-1.2
3. **Cost tracking** - Shows Claude tokens + ElevenLabs characters
4. **Voice swap** - Female=Lead (Speaker A), Male=Skeptic (Speaker B)
5. **Dutch support** - All 3 templates in NL
6. **Filename** - `{project}_{topic}_{lang}_{date}_{MODE}.mp3`
