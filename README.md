# AI Podcast Pipeline

Generate podcasts with Claude research + ElevenLabs audio.

## File Structure

```
myfirstpodcast/
├── podcast_pipeline.py          # Main script
├── smart_update.sh               # Update automation (chmod +x)
├── requirements.txt              # Dependencies
├── config/
│   ├── .env                      # API keys (YOU create)
│   └── podcast_config.json       # Voice IDs, styles, languages
├── templates/
│   ├── popular_science_{language}_dynamic.txt
│   ├── technical_deep_dive_{language}.txt
│   ├── news_brief_{language}.txt
│   └── research_contexts/
│       └── default.txt           # Reusable research template (YOU create)
└── projects/                     # Created by script
    └── {project_name}/
        ├── prompts/              # Prompt versions
        ├── sources/
        │   ├── research_context.txt   # Project-specific or default
        │   └── sources_list.txt       # Available sources
        ├── scripts/
        │   ├── {name}_draft1.txt      # Generated scripts
        │   └── {name}_sources.txt     # Extracted sources
        ├── audio/
        │   └── {project}_{topic}_{lang}_{date}_{MODE}.mp3
        └── debug/
            └── chunk_*_content.json   # Debug info
```

## User Flow

1. **Run:** `python podcast_pipeline.py`

2. **Enter:** 
   - Project name (folder/file names, alphanumeric)
   - Podcast topic (content, allows spaces)
   - Duration (minutes)

3. **Select style:**
   ```
   1. Dynamic, friendly science communication
   2. In-depth technical analysis for experts
   3. Quick news update format
   ```

4. **Select language:**
   ```
   1. Deutsch (German) - DE
   2. English - EN
   3. Nederlands (Dutch) - NL
   ```

5. **Select mode:**
   ```
   1. Prototype (lower quality, testing)
   2. Production (full quality, final)
   ```

6. **Research context:**
   ```
   1. Use as-is (proceed with current context)
   2. Edit current context (customize for this project)
   3. Reset to default template
   4. Show current context
   ```

7. **Review prompt:** Edit or confirm

8. **Source documents (NEW):**
   ```
   1. Proceed (use existing documents if any)
   2. List and read current documents
   3. Add new source files
   ```
   - Add your PDFs, Word docs, PowerPoints to `projects/{project}/sources/`
   - Claude uses them alongside web research

9. **Claude generates:** Script with web research + your documents

10. **Review script:**
   ```
   1. Open script in text editor to review
   2. Approve script and proceed to audio
   3. Ask Claude to revise
   4. Edit script file manually, then regenerate
   5. Save prompt variant to project
   6. Cancel
   ```

11. **Generate audio:** ElevenLabs creates MP3

12. **Output:** `projects/{project}/{project}_{topic}_{lang}_{date}_{MODE}.mp3`

## Quick Reference

**Setup:** See [SETUP_UPDATE.md](SETUP_UPDATE.md)

**Key Features:**
- `[audio tags]` for emotions ([excited], [laughs], etc.)
- Research contexts (default + project-specific)
- **Source documents** - Add PDFs/Word/PowerPoint to research
- Auto-saves sources separately (not in audio)
- Debug chunks for troubleshooting
- Smart updates preserve everything
- Multi-language support (DE/EN/NL)
- Template selection (popular science, technical, news)

**Post-Processing Tools:**
- `translate_script.py` - Translate scripts to another language
- `tune_audio.py` - Adjust speaker speeds independently

**Supported Source Documents:**
- Text: `.txt`, `.md`
- Documents: `.docx`
- PDF: `.pdf`
- Presentations: `.pptx`

**Audio Files:**
- Prototype: 64k bitrate, downsampled (testing)
- Production: High quality, no downsampling (final)
- Filename: `{project}_{topic}_{lang}_{date}_{MODE}.mp3`

**Languages:**
- German (DE): Voice IDs in config
- English (EN): Voice IDs in config
- Dutch (NL): Voice IDs in config

**Templates:**
- Popular science: Dynamic, friendly (15 min)
- Technical deep dive: Expert-level (20 min)
- News brief: Quick update (5 min)
- Each available in DE, EN, NL

Done.

