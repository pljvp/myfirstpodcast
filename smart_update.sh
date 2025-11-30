#!/bin/bash
# smart_update.sh - Handles providers/ folder and multi-file updates
# FIXED: Now handles tune_audio and translate_script properly

set -e

echo "=== SMART PODCAST PIPELINE UPDATE ==="
echo ""

# Check location
if [ ! -f "podcast_pipeline.py" ]; then
    echo "❌ ERROR: Run this from your myfirstpodcast folder"
    exit 1
fi

# Create backup directories
BACKUP_DIR=".update_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
mkdir -p ".backup"

echo "📦 BACKING UP YOUR DATA..."
echo ""

# Backup configs
echo "  → API keys & config..."
cp config/.env "$BACKUP_DIR/.env" 2>/dev/null || echo "    (No .env found)"
cp config/podcast_config.json "$BACKUP_DIR/podcast_config.json"

# Backup templates
if [ -d "templates/research_contexts" ]; then
    echo "  → Research templates..."
    mkdir -p "$BACKUP_DIR/research_contexts"
    cp -r templates/research_contexts/* "$BACKUP_DIR/research_contexts/" 2>/dev/null || true
fi

mkdir -p "$BACKUP_DIR/templates"
cp templates/*.txt "$BACKUP_DIR/templates/" 2>/dev/null || true

# Backup project contexts
echo "  → Project contexts..."
mkdir -p "$BACKUP_DIR/project_contexts"
for project_dir in projects/*/; do
    if [ -d "$project_dir" ]; then
        project_name=$(basename "$project_dir")
        if [ -f "$project_dir/sources/research_context.txt" ]; then
            mkdir -p "$BACKUP_DIR/project_contexts/$project_name"
            cp "$project_dir/sources/research_context.txt" "$BACKUP_DIR/project_contexts/$project_name/"
        fi
    fi
done

echo "✓ Backed up to: $BACKUP_DIR"
echo ""

# Update pipeline
echo "📥 CHECKING FOR UPDATES..."
echo ""
echo "Looking for pipeline files:"
echo "  - podcast_pipeline_UPDATED.py"
echo "  - podcast_pipeline_NEW.py"
echo "  - podcast_pipeline_new.py"
echo "  - podcast_pipeline_FIXED.py"
echo ""

PIPELINE_UPDATED=false

# Check for pipeline files (_UPDATED, _NEW, _new, _FIXED)
for suffix in "_UPDATED" "_NEW" "_new" "_FIXED"; do
    if [ -f "podcast_pipeline${suffix}.py" ]; then
        echo "  ✓ FOUND: podcast_pipeline${suffix}.py"
        OLD_BACKUP=".backup/podcast_pipeline_backup_$(date +%Y%m%d_%H%M%S).py"
        mv podcast_pipeline.py "$OLD_BACKUP"
        mv "podcast_pipeline${suffix}.py" podcast_pipeline.py
        echo "  ✓ INSTALLED (old → $OLD_BACKUP)"
        PIPELINE_UPDATED=true
        break
    fi
done

if [ "$PIPELINE_UPDATED" = false ]; then
    echo "  ❌ NO PIPELINE FILE FOUND"
    echo ""
    echo "Expected: podcast_pipeline_UPDATED.py, _NEW.py, _new.py, or _FIXED.py"
    read -p "Continue? (y/N): " continue_choice
    if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
        exit 1
    fi
fi

# Handle providers folder
echo ""
echo "Looking for providers/ folder..."
if [ -d "providers" ]; then
    echo "  ✓ FOUND: providers/ folder"
    
    # Backup existing if present
    if [ -d "providers" ] && [ "$(ls -A providers 2>/dev/null)" ]; then
        PROVIDERS_BACKUP=".backup/providers_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$PROVIDERS_BACKUP"
        cp -r providers/* "$PROVIDERS_BACKUP/" 2>/dev/null
        echo "    (backed up to $PROVIDERS_BACKUP)"
    fi
    
    echo "  ✓ Providers installed"
    PROVIDERS_UPDATED=true
else
    echo "  ➖ No providers/ folder found"
    PROVIDERS_UPDATED=false
fi

# Handle utility scripts
echo ""
echo "Looking for utility scripts:"
echo "  - tune_audio_UPDATED.py / _NEW.py / _new.py / _FIXED.py"
echo "  - translate_script_UPDATED.py / _NEW.py / _new.py / _FIXED.py"
echo ""

UTILITIES_UPDATED=0

# Handle tune_audio
TUNE_FOUND=false
for suffix in "_UPDATED" "_NEW" "_new" "_FIXED"; do
    if [ -f "tune_audio${suffix}.py" ]; then
        echo "  ✓ FOUND: tune_audio${suffix}.py"
        if [ -f "tune_audio.py" ]; then
            OLD_BACKUP=".backup/tune_audio_backup_$(date +%Y%m%d_%H%M%S).py"
            mv tune_audio.py "$OLD_BACKUP"
            echo "    (backed up to $OLD_BACKUP)"
        fi
        mv "tune_audio${suffix}.py" tune_audio.py
        chmod +x tune_audio.py
        echo "  ✓ INSTALLED: tune_audio.py"
        UTILITIES_UPDATED=$((UTILITIES_UPDATED + 1))
        TUNE_FOUND=true
        break
    fi
done

if [ "$TUNE_FOUND" = false ]; then
    echo "  ➖ tune_audio (not found - optional)"
fi

# Handle translate_script
TRANSLATE_FOUND=false
for suffix in "_UPDATED" "_NEW" "_new" "_FIXED"; do
    if [ -f "translate_script${suffix}.py" ]; then
        echo "  ✓ FOUND: translate_script${suffix}.py"
        if [ -f "translate_script.py" ]; then
            OLD_BACKUP=".backup/translate_script_backup_$(date +%Y%m%d_%H%M%S).py"
            mv translate_script.py "$OLD_BACKUP"
            echo "    (backed up to $OLD_BACKUP)"
        fi
        mv "translate_script${suffix}.py" translate_script.py
        chmod +x translate_script.py
        echo "  ✓ INSTALLED: translate_script.py"
        UTILITIES_UPDATED=$((UTILITIES_UPDATED + 1))
        TRANSLATE_FOUND=true
        break
    fi
done

if [ "$TRANSLATE_FOUND" = false ]; then
    echo "  ➖ translate_script (not found - optional)"
fi

# Handle config
echo ""
if [ -f "podcast_config_UPDATED.json" ]; then
    echo "  ⚠️  New config structure detected"
    echo "  → Contains provider configuration for ElevenLabs + Cartesia"
    read -p "Replace config? (y/N): " config_choice
    if [ "$config_choice" == "y" ] || [ "$config_choice" == "Y" ]; then
        CONFIG_BACKUP=".backup/podcast_config_backup_$(date +%Y%m%d_%H%M%S).json"
        mv "config/podcast_config.json" "$CONFIG_BACKUP"
        mv "podcast_config_UPDATED.json" "config/podcast_config.json"
        echo "  ✓ Config updated (old → $CONFIG_BACKUP)"
        echo ""
        echo "  ⚠️  IMPORTANT: Edit config/podcast_config.json to add:"
        echo "     - Your Cartesia voice IDs (replace placeholders)"
    else
        echo "  ➖ Keeping existing config"
        rm "podcast_config_UPDATED.json"
    fi
elif [ -f "podcast_config.json" ]; then
    echo "  ✓ FOUND: podcast_config.json (moving to config/)"
    mv "podcast_config.json" "config/"
fi

# Handle requirements
if [ -f "requirements_UPDATED.txt" ]; then
    echo ""
    echo "  ✓ FOUND: requirements_UPDATED.txt"
    REQ_BACKUP=".backup/requirements_backup_$(date +%Y%m%d_%H%M%S).txt"
    cp "requirements.txt" "$REQ_BACKUP" 2>/dev/null || true
    mv "requirements_UPDATED.txt" "requirements.txt"
    echo "  ✓ Requirements updated (old → $REQ_BACKUP)"
    echo ""
    echo "  💡 Run: pip install -r requirements.txt --break-system-packages"
fi

# Restore data
echo ""
echo "📦 RESTORING YOUR DATA..."
cp "$BACKUP_DIR/.env" config/.env 2>/dev/null || true

if [ -d "$BACKUP_DIR/research_contexts" ]; then
    mkdir -p templates/research_contexts
    cp -r "$BACKUP_DIR/research_contexts"/* templates/research_contexts/ 2>/dev/null || true
fi

if [ -d "$BACKUP_DIR/project_contexts" ]; then
    for project_dir in "$BACKUP_DIR/project_contexts"/*; do
        if [ -d "$project_dir" ]; then
            project_name=$(basename "$project_dir")
            if [ -f "$project_dir/research_context.txt" ]; then
                mkdir -p "projects/$project_name/sources"
                cp "$project_dir/research_context.txt" "projects/$project_name/sources/"
            fi
        fi
    done
fi

echo ""
echo "="*60
if [ "$PIPELINE_UPDATED" = true ]; then
    echo "✅ UPDATE COMPLETE!"
    if [ "$PROVIDERS_UPDATED" = true ]; then
        echo "✅ Provider system installed!"
    fi
    if [ $UTILITIES_UPDATED -gt 0 ]; then
        echo "✅ Updated $UTILITIES_UPDATED utility script(s)"
    fi
else
    echo "⚠️  PARTIAL UPDATE"
fi
echo "="*60
echo ""
echo "Summary:"
if [ "$PIPELINE_UPDATED" = true ]; then
    echo "  ✅ Pipeline script"
else
    echo "  ❌ Pipeline script (not found)"
fi
if [ "$PROVIDERS_UPDATED" = true ]; then
    echo "  ✅ TTS providers/ folder"
fi
if [ $UTILITIES_UPDATED -gt 0 ]; then
    echo "  ✅ Utility scripts ($UTILITIES_UPDATED)"
fi
echo "  ✅ API keys preserved"
echo "  ✅ Templates preserved"
echo "  ✅ Projects preserved"
echo ""
echo "✓ Ready: python podcast_pipeline.py"
echo ""
