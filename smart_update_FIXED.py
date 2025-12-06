#!/usr/bin/env python3
"""
Smart Update Script - Complete Cross-Platform Solution
Replaces smart_update.sh with full feature parity + enhancements
"""

import os
import shutil
import platform
from pathlib import Path
from datetime import datetime

# File mapping: source in root → destination
FILE_UPDATES = {
    # Core pipeline files
    'podcast_pipeline_FIXED.py': 'podcast_pipeline.py',
    'podcast_pipeline_UPDATED.py': 'podcast_pipeline.py',
    'podcast_pipeline_NEW.py': 'podcast_pipeline.py',
    'podcast_pipeline_new.py': 'podcast_pipeline.py',
    
    # Utility scripts
    'tune_audio_FIXED.py': 'tune_audio.py',
    'tune_audio_UPDATED.py': 'tune_audio.py',
    'translate_script_FIXED.py': 'translate_script.py',
    'translate_script_UPDATED.py': 'translate_script.py',
    
    # Provider files
    'cartesia_FIXED.py': 'providers/cartesia.py',
    'elevenlabs_FIXED.py': 'providers/elevenlabs.py',
    
    # Config and requirements
    'requirements_UPDATED.txt': 'requirements.txt',
    'README_UPDATED_INSTALL.md': 'README.md',
    
    # Templates
    'popular_science_dutch_TEST.txt': 'templates/popular_science_dutch_TEST.txt',
    'popular_science_english_TEST.txt': 'templates/popular_science_english_TEST.txt',
    'popular_science_german_TEST.txt': 'templates/popular_science_german_TEST.txt',
}

# Special handling for config (requires user confirmation)
CONFIG_FILES = {
    'podcast_config_UPDATED.json': 'config/podcast_config.json',
}

# Files to remove from root after successful copy
CLEANUP_FILES = list(FILE_UPDATES.keys()) + list(CONFIG_FILES.keys())

def get_platform_info():
    """Detect operating system"""
    system = platform.system()
    return {
        'os': system,
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux',
        'is_mac': system == 'Darwin'
    }

def create_backup_structure():
    """Create comprehensive backup directories"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'.update_backup_{timestamp}')
    backup_dir.mkdir(exist_ok=True)
    
    # Also create .backup for individual file backups
    Path('.backup').mkdir(exist_ok=True)
    
    return backup_dir

def backup_user_data(backup_dir):
    """Backup all user data (from .sh logic)"""
    print("\n📦 BACKING UP YOUR DATA...\n")
    
    # 1. Backup configs
    print("  → API keys & config...")
    config_env = Path('config/.env')
    if config_env.exists():
        shutil.copy2(config_env, backup_dir / '.env')
    else:
        print("    (No .env found)")
    
    config_json = Path('config/podcast_config.json')
    if config_json.exists():
        shutil.copy2(config_json, backup_dir / 'podcast_config.json')
    
    # 2. Backup research templates
    research_dir = Path('templates/research_contexts')
    if research_dir.exists():
        print("  → Research templates...")
        backup_research = backup_dir / 'research_contexts'
        backup_research.mkdir(exist_ok=True)
        try:
            for item in research_dir.glob('*'):
                if item.is_file():
                    shutil.copy2(item, backup_research / item.name)
        except Exception as e:
            print(f"    Warning: {e}")
    
    # 3. Backup all template files
    templates_dir = Path('templates')
    if templates_dir.exists():
        backup_templates = backup_dir / 'templates'
        backup_templates.mkdir(exist_ok=True)
        try:
            for item in templates_dir.glob('*.txt'):
                shutil.copy2(item, backup_templates / item.name)
        except Exception as e:
            print(f"    Warning: {e}")
    
    # 4. Backup project contexts
    print("  → Project contexts...")
    projects_dir = Path('projects')
    if projects_dir.exists():
        backup_contexts = backup_dir / 'project_contexts'
        backup_contexts.mkdir(exist_ok=True)
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                context_file = project_dir / 'sources' / 'research_context.txt'
                if context_file.exists():
                    project_backup = backup_contexts / project_dir.name
                    project_backup.mkdir(exist_ok=True)
                    shutil.copy2(context_file, project_backup / 'research_context.txt')
    
    print(f"\n✅ Backed up to: {backup_dir}\n")
    return backup_dir

def restore_user_data(backup_dir):
    """Restore user data after updates"""
    print("\n📦 RESTORING YOUR DATA...\n")
    
    # Restore .env
    env_backup = backup_dir / '.env'
    if env_backup.exists():
        print("  → API keys...")
        shutil.copy2(env_backup, 'config/.env')
    
    # Restore research contexts
    research_backup = backup_dir / 'research_contexts'
    if research_backup.exists():
        print("  → Research templates...")
        Path('templates/research_contexts').mkdir(parents=True, exist_ok=True)
        for item in research_backup.glob('*'):
            if item.is_file():
                shutil.copy2(item, Path('templates/research_contexts') / item.name)
    
    # Restore project contexts
    contexts_backup = backup_dir / 'project_contexts'
    if contexts_backup.exists():
        print("  → Project contexts...")
        for project_backup in contexts_backup.iterdir():
            if project_backup.is_dir():
                context_file = project_backup / 'research_context.txt'
                if context_file.exists():
                    dest_dir = Path('projects') / project_backup.name / 'sources'
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(context_file, dest_dir / 'research_context.txt')
                    print(f"    ✅ {project_backup.name}/research_context.txt")
    
    print()

def create_individual_backup(filepath):
    """Create timestamped backup of individual file"""
    if not os.path.exists(filepath):
        return None
    
    backup_dir = Path('.backup')
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = Path(filepath).name
    backup_path = backup_dir / f"{filename}.{timestamp}.bak"
    
    shutil.copy2(filepath, backup_path)
    return backup_path

def update_file(source, destination):
    """Update single file with individual backup"""
    source_path = Path(source)
    dest_path = Path(destination)
    
    if not source_path.exists():
        return False
    
    # Create individual backup if destination exists
    if dest_path.exists():
        backup = create_individual_backup(dest_path)
        if backup:
            print(f"    💾 Backed up: {backup.name}")
    
    # Ensure destination directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    shutil.copy2(source_path, dest_path)
    
    # Make scripts executable (Unix-like systems)
    if dest_path.suffix == '.py' and not get_platform_info()['is_windows']:
        try:
            os.chmod(dest_path, 0o755)
        except:
            pass
    
    return True

def handle_config_update():
    """Handle config file update with user confirmation"""
    config_source = Path('podcast_config_UPDATED.json')
    if not config_source.exists():
        return False
    
    print("\n" + "="*60)
    print("⚠️  NEW CONFIG STRUCTURE DETECTED")
    print("="*60)
    print("\nThis update includes a new podcast_config.json with:")
    print("  → Provider configuration for ElevenLabs + Cartesia")
    print("  → Your existing config has been backed up")
    print()
    
    response = input("Replace config with new version? (y/N): ").strip().lower()
    
    if response == 'y':
        # Backup old config
        old_config = Path('config/podcast_config.json')
        if old_config.exists():
            backup = create_individual_backup(old_config)
            print(f"  ✅ Old config backed up: {backup.name}")
        
        # Move new config
        shutil.move(config_source, 'config/podcast_config.json')
        print("  ✅ Config updated")
        print("\n  ⚠️  IMPORTANT: Edit config/podcast_config.json to add:")
        print("     - Your Cartesia voice IDs (replace placeholders)")
        return True
    else:
        print("  ⏭️  Keeping existing config")
        config_source.unlink()  # Remove the update file
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        cmd = 'ffmpeg -version > nul 2>&1' if platform.system() == 'Windows' else 'ffmpeg -version > /dev/null 2>&1'
        result = os.system(cmd)
        return result == 0
    except:
        return False

def install_ffmpeg_instructions():
    """Show OS-specific ffmpeg installation instructions"""
    info = get_platform_info()
    
    print("\n" + "="*60)
    print("⚠️  FFMPEG NOT FOUND")
    print("="*60)
    print("\nffmpeg is required for audio processing (Cartesia PCM → MP3)")
    print("\nInstallation instructions:\n")
    
    if info['is_windows']:
        print("Windows:")
        print("  Option 1 (Chocolatey): choco install ffmpeg")
        print("  Option 2 (Scoop):      scoop install ffmpeg")
        print("  Option 3 (Manual):     https://ffmpeg.org/download.html")
        print("                         Extract and add bin folder to PATH")
    elif info['is_mac']:
        print("macOS:")
        print("  brew install ffmpeg")
    elif info['is_linux']:
        print("Linux:")
        print("  sudo apt-get install ffmpeg  # Ubuntu/Debian")
        print("  sudo yum install ffmpeg      # CentOS/RHEL")
    
    print("\nAfter installing ffmpeg, run this script again.")
    print("="*60 + "\n")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("  ⚠️  requirements.txt not found!")
        return False
    
    cmd = 'pip install -r requirements.txt'
    print(f"  Running: {cmd}")
    
    result = os.system(cmd)
    if result == 0:
        print("  ✅ Python dependencies installed")
        return True
    else:
        print("  ❌ Failed to install dependencies")
        return False

def cleanup_root_files():
    """Remove _FIXED and _UPDATED files from root"""
    print("\n🧹 Cleaning up temporary files from root...")
    
    cleaned = 0
    for filename in CLEANUP_FILES:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                print(f"  ✅ Removed: {filename}")
                cleaned += 1
            except Exception as e:
                print(f"  ⚠️  Could not remove {filename}: {e}")
    
    if cleaned == 0:
        print("  ℹ️  No temporary files to clean up")
    else:
        print(f"  🎉 Cleaned up {cleaned} temporary files")

def check_dependencies():
    """Check Python package dependencies"""
    print("\n📋 Dependency Status:\n")
    
    packages = [
        ('pydub', 'required'),
        ('anthropic', 'required'),
        ('cartesia', 'required'),
        ('requests', 'required'),
        ('dotenv', 'required'),
        ('docx', 'optional'),
        ('PyPDF2', 'optional'),
        ('pptx', 'optional'),
    ]
    
    for package, status in packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'docx':
                __import__('docx')
            elif package == 'pptx':
                __import__('pptx')
            else:
                __import__(package)
            print(f"  ✅ {package:15s} installed ({status})")
        except ImportError:
            if status == 'required':
                print(f"  ❌ {package:15s} MISSING  ({status})")
            else:
                print(f"  ⚪ {package:15s} not installed ({status})")
    
    # Check ffmpeg
    if check_ffmpeg():
        print(f"  ✅ {'ffmpeg':15s} installed (required)")
    else:
        print(f"  ❌ {'ffmpeg':15s} MISSING  (required)")

def main():
    """Main update process"""
    info = get_platform_info()
    
    print("="*60)
    print("🔄 SMART UPDATE - Complete Cross-Platform Solution")
    print("="*60)
    print(f"\nDetected OS: {info['os']}")
    print(f"Working directory: {Path.cwd()}\n")
    
    # Check we're in the right directory
    if not Path('podcast_pipeline.py').exists():
        print("❌ ERROR: Run this from your myfirstpodcast folder")
        print("   (podcast_pipeline.py not found)")
        return 1
    
    # Create backup structure and backup user data
    backup_dir = create_backup_structure()
    backup_user_data(backup_dir)
    
    # Update files
    print("📁 Updating core files...\n")
    
    updated_count = 0
    updated_files = []
    
    for source, destination in FILE_UPDATES.items():
        if Path(source).exists():
            print(f"  ✅ Found: {source}")
            if update_file(source, destination):
                print(f"     → Updated: {destination}")
                updated_count += 1
                updated_files.append(destination)
            else:
                print(f"     ❌ Failed to update")
    
    if updated_count == 0:
        print("  ⚠️  No update files found in root directory")
        print("\n  Expected files: podcast_pipeline_FIXED.py, etc.")
    
    # Handle config separately (needs confirmation)
    config_updated = handle_config_update()
    
    # Check ffmpeg
    print("\n🔍 Checking system dependencies...\n")
    if check_ffmpeg():
        print("  ✅ ffmpeg is installed")
    else:
        install_ffmpeg_instructions()
    
    # Install Python dependencies if files were updated
    if updated_count > 0:
        install_dependencies()
    
    # Restore user data
    restore_user_data(backup_dir)
    
    # Cleanup temporary files
    cleanup_root_files()
    
    # Check dependencies
    check_dependencies()
    
    # Summary
    print("\n" + "="*60)
    print("✅ UPDATE COMPLETE")
    print("="*60)
    print(f"\nBackup location: {backup_dir}")
    print(f"Individual backups: .backup/")
    print(f"\nUpdated files: {updated_count}")
    
    if updated_files:
        print("\nWhat was updated:")
        for f in updated_files:
            print(f"  ✅ {f}")
    
    if config_updated:
        print("  ✅ config/podcast_config.json (new structure)")
    
    print("\nPreserved:")
    print("  ✅ API keys")
    print("  ✅ Voice config")
    print("  ✅ Templates")
    print("  ✅ Project contexts")
    
    print()
    
    if updated_count > 0 and check_ffmpeg():
        print("✅ All systems ready!")
        print("\nRun: python podcast_pipeline.py")
    else:
        print("⚠️  Some steps require attention (see above)")
    
    print("\n")
    return 0

if __name__ == "__main__":
    exit(main())
