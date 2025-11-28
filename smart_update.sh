#!/bin/bash
# smart_update.sh - Intelligent pipeline update with full preservation

set -e

echo "=== SMART PODCAST PIPELINE UPDATE ==="
echo ""

# Check location
if [ ! -f "podcast_pipeline.py" ]; then
    echo "❌ ERROR: Run this from your myfirstpodcast_v3 folder"
    exit 1
fi

# Create backup directories
BACKUP_DIR=".update_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
mkdir -p ".backup"

echo "📦 BACKING UP YOUR DATA..."
echo ""

# 1. Backup configs
echo "  → API keys & voice IDs..."
cp config/.env "$BACKUP_DIR/.env" 2>/dev/null || echo "    (No .env found)"
cp config/podcast_config.json "$BACKUP_DIR/podcast_config.json"

# 2. Backup research templates
if [ -d "templates/research_contexts" ]; then
    echo "  → Research context templates..."
    mkdir -p "$BACKUP_DIR/research_contexts"
    cp -r templates/research_contexts/* "$BACKUP_DIR/research_contexts/" 2>/dev/null || true
fi

# 3. Backup all template files
echo "  → Podcast templates..."
mkdir -p "$BACKUP_DIR/templates"
cp templates/*.txt "$BACKUP_DIR/templates/" 2>/dev/null || true

# 4. Backup project contexts
echo "  → Project-specific research contexts..."
mkdir -p "$BACKUP_DIR/project_contexts"
for project_dir in projects/*/; do
    if [ -d "$project_dir" ]; then
        project_name=$(basename "$project_dir")
        if [ -f "$project_dir/sources/research_context.txt" ]; then
            mkdir -p "$BACKUP_DIR/project_contexts/$project_name"
            cp "$project_dir/sources/research_context.txt" "$BACKUP_DIR/project_contexts/$project_name/"
            echo "    ✓ Backed up: $project_name/research_context.txt"
        fi
    fi
done

echo ""
echo "✓ All data backed up to: $BACKUP_DIR"
echo ""

# 5. Update files
echo "📥 CHECKING FOR NEW FILES..."
echo ""

# Show what we're looking for and what we found
echo "Looking for pipeline files:"
echo "  - podcast_pipeline_FIXED.py"
echo "  - podcast_pipeline_new.py"
echo ""

PIPELINE_UPDATED=false

# Handle pipeline files
if [ -f "podcast_pipeline_FIXED.py" ]; then
    echo "  ✓ FOUND: podcast_pipeline_FIXED.py"
    OLD_BACKUP=".backup/podcast_pipeline_backup_$(date +%Y%m%d_%H%M%S).py"
    mv podcast_pipeline.py "$OLD_BACKUP"
    mv podcast_pipeline_FIXED.py podcast_pipeline.py
    echo "  ✓ INSTALLED: podcast_pipeline.py (old saved to $OLD_BACKUP)"
    PIPELINE_UPDATED=true
elif [ -f "podcast_pipeline_new.py" ]; then
    echo "  ✓ FOUND: podcast_pipeline_new.py"
    OLD_BACKUP=".backup/podcast_pipeline_backup_$(date +%Y%m%d_%H%M%S).py"
    mv podcast_pipeline.py "$OLD_BACKUP"
    mv podcast_pipeline_new.py podcast_pipeline.py
    echo "  ✓ INSTALLED: podcast_pipeline.py (old saved to $OLD_BACKUP)"
    PIPELINE_UPDATED=true
else
    echo "  ❌ NO PIPELINE FILE FOUND"
    echo ""
    echo "Put one of these files in this folder:"
    echo "  - podcast_pipeline_FIXED.py"
    echo "  - podcast_pipeline_new.py"
    echo ""
    ls -la *.py 2>/dev/null | grep -v "__" || echo "No .py files found in current directory"
    echo ""
    read -p "Continue anyway? (y/N): " continue_choice
    if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

echo ""
echo "Looking for utility scripts:"
echo "  - translate_script.py"
echo "  - tune_audio.py"
echo ""

UTILITIES_UPDATED=0

# Handle translate_script.py
if [ -f "translate_script.py" ]; then
    echo "  ✓ FOUND: translate_script.py"
    if [ -f "./translate_script.py" ] && [ ! -L "./translate_script.py" ]; then
        # Backup existing if it's a real file (not a new install)
        if [ -s "./translate_script.py" ]; then
            OLD_BACKUP=".backup/translate_script_backup_$(date +%Y%m%d_%H%M%S).py"
            cp ./translate_script.py "$OLD_BACKUP" 2>/dev/null
            echo "    (backed up to $OLD_BACKUP)"
        fi
    fi
    chmod +x translate_script.py
    echo "  ✓ INSTALLED: translate_script.py (executable)"
    UTILITIES_UPDATED=$((UTILITIES_UPDATED + 1))
fi

# Handle tune_audio.py
if [ -f "tune_audio.py" ]; then
    echo "  ✓ FOUND: tune_audio.py"
    if [ -f "./tune_audio.py" ] && [ ! -L "./tune_audio.py" ]; then
        # Backup existing if it's a real file
        if [ -s "./tune_audio.py" ]; then
            OLD_BACKUP=".backup/tune_audio_backup_$(date +%Y%m%d_%H%M%S).py"
            cp ./tune_audio.py "$OLD_BACKUP" 2>/dev/null
            echo "    (backed up to $OLD_BACKUP)"
        fi
    fi
    chmod +x tune_audio.py
    echo "  ✓ INSTALLED: tune_audio.py (executable)"
    UTILITIES_UPDATED=$((UTILITIES_UPDATED + 1))
fi

if [ $UTILITIES_UPDATED -eq 0 ]; then
    echo "  (No utility scripts found - this is optional)"
fi

echo ""
echo "Processing template files..."

# Handle template files with _FIXED suffix
TEMPLATES_MOVED=0
for file in *_FIXED.txt; do
    if [ -f "$file" ] && [ "$file" != "*_FIXED.txt" ]; then
        target=$(echo "$file" | sed 's/_FIXED//')
        mv "$file" "templates/$target"
        echo "  ✓ $file → templates/$target"
        TEMPLATES_MOVED=$((TEMPLATES_MOVED + 1))
    fi
done

# Handle loose template files in root
for file in news_brief_*.txt technical_deep_dive_*.txt popular_science_*.txt; do
    if [ -f "$file" ] && [ "$file" != "*_*.txt" ]; then
        mv "$file" "templates/"
        echo "  ✓ $file → templates/"
        TEMPLATES_MOVED=$((TEMPLATES_MOVED + 1))
    fi
done

if [ $TEMPLATES_MOVED -eq 0 ]; then
    echo "  (No template files to move)"
fi

# Handle config file if in root
if [ -f "podcast_config.json" ]; then
    echo ""
    echo "  ✓ FOUND: podcast_config.json"
    mv "podcast_config.json" "config/"
    echo "  ✓ MOVED: config/podcast_config.json"
fi

echo ""
echo "📦 RESTORING YOUR DATA..."
echo ""

# 6. Restore configs
echo "  → API keys..."
cp "$BACKUP_DIR/.env" config/.env 2>/dev/null || echo "    (No .env to restore)"
echo "    ✓ Configs restored"

# 7. Restore research templates
if [ -d "$BACKUP_DIR/research_contexts" ]; then
    echo "  → Research templates..."
    mkdir -p templates/research_contexts
    cp -r "$BACKUP_DIR/research_contexts"/* templates/research_contexts/ 2>/dev/null || true
    echo "    ✓ Restored"
fi

# 8. Restore project contexts
echo "  → Project contexts..."
if [ -d "$BACKUP_DIR/project_contexts" ]; then
    for project_dir in "$BACKUP_DIR/project_contexts"/*; do
        if [ -d "$project_dir" ]; then
            project_name=$(basename "$project_dir")
            if [ -f "$project_dir/research_context.txt" ]; then
                mkdir -p "projects/$project_name/sources"
                cp "$project_dir/research_context.txt" "projects/$project_name/sources/"
                echo "    ✓ $project_name/research_context.txt"
            fi
        fi
    done
fi

echo ""
echo "="*60
if [ "$PIPELINE_UPDATED" = true ]; then
    echo "✅ UPDATE COMPLETE!"
else
    echo "⚠️  UPDATE PARTIAL - NO PIPELINE FILE UPDATED"
fi
echo "="*60
echo "Backup: $BACKUP_DIR"
echo "Pipeline backups: .backup/"
echo ""
echo "What was updated:"
if [ "$PIPELINE_UPDATED" = true ]; then
    echo "  ✅ Pipeline script"
else
    echo "  ❌ Pipeline script (not found)"
fi
if [ $UTILITIES_UPDATED -gt 0 ]; then
    echo "  ✅ $UTILITIES_UPDATED utility script(s) (translate/tune)"
else
    echo "  ➖ Utility scripts (not found - optional)"
fi
echo "  ✅ API keys preserved"
echo "  ✅ Voice config preserved"
echo "  ✅ Templates preserved"
echo "  ✅ Project contexts preserved"
if [ $TEMPLATES_MOVED -gt 0 ]; then
    echo "  ✅ $TEMPLATES_MOVED template file(s) moved"
fi
echo ""
if [ "$PIPELINE_UPDATED" = true ]; then
    echo "✓ Ready to run: python podcast_pipeline.py"
    if [ $UTILITIES_UPDATED -gt 0 ]; then
        echo "✓ New utilities available: translate_script.py, tune_audio.py"
    fi
else
    echo "⚠️  Pipeline not updated - download podcast_pipeline_FIXED.py first!"
fi
echo ""
