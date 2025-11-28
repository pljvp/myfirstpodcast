#!/usr/bin/env python3
"""
AI Podcast Pipeline v3.0 - Enhanced Debug Mode
- Better error logging
- Shows WHY retry is happening
- Verbose mode for troubleshooting
"""

import os
import json
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
import requests

# Document reading libraries (optional - graceful fallback if not installed)
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

# Load environment variables
config_path = Path(__file__).parent / 'config' / '.env'
load_dotenv(config_path)

# Debug mode - set to True for verbose logging
DEBUG_VERBOSE = True


def log_debug(message):
    """Print debug message if verbose mode enabled"""
    if DEBUG_VERBOSE:
        print(f"[VERBOSE] {message}")


def load_config():
    """Load podcast_config.json from config folder"""
    config_file = Path(__file__).parent / 'config' / 'podcast_config.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_project_structure(project_name):
    """Create project folder with subdirectories"""
    base_path = Path(f"./projects/{project_name}")
    (base_path / "prompts").mkdir(parents=True, exist_ok=True)
    (base_path / "sources").mkdir(parents=True, exist_ok=True)
    (base_path / "scripts").mkdir(parents=True, exist_ok=True)
    (base_path / "audio").mkdir(parents=True, exist_ok=True)
    (base_path / "debug").mkdir(parents=True, exist_ok=True)
    
    sources_file = base_path / "sources" / "sources_list.txt"
    if not sources_file.exists():
        with open(sources_file, 'w', encoding='utf-8') as f:
            f.write(f"Research Sources for {project_name}\n\n")
            f.write("Primary Sources:\n- \n\n")
            f.write("Background Reading:\n- \n\n")
            f.write("Key Points to Cover:\n- \n")
    
    context_file = base_path / "sources" / "research_context.txt"
    if not context_file.exists():
        # Check if there's a default template to use
        default_template = Path("templates/research_contexts/default.txt")
        
        if default_template.exists():
            log_debug(f"Using default research context template: {default_template}")
            with open(default_template, 'r', encoding='utf-8') as f:
                template_content = f.read()
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(template_content.replace("{project_name}", project_name))
            print(f"  ✓ Using default research context template")
        else:
            # Create minimal default
            log_debug("No template found, creating minimal default")
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(f"Research Context for {project_name}\n\n")
                f.write("=== RESEARCH INSTRUCTIONS ===\n")
                f.write("Number of sources to find: 5-10\n")
                f.write("Focus on recent (2024-2025) developments\n\n")
                f.write("=== CONTEXT AND FOCUS AREAS ===\n")
                f.write("(Describe what Claude should focus on during research)\n\n")
                f.write("=== SPECIFIC QUESTIONS TO ANSWER ===\n")
                f.write("1. What are the latest developments?\n")
                f.write("2. What are the practical applications?\n")
                f.write("3. What are experts saying?\n\n")
                f.write("=== AUDIENCE CONSIDERATIONS ===\n")
                f.write("Intelligent general audience - explain jargon, use analogies\n")
    else:
        print(f"  ✓ Using existing research context (project-specific)")
    
    return base_path


def load_template(template_path, variables):
    """Load template and substitute variables"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    for key, value in variables.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def get_user_input(prompt, options=None):
    """Get user input with optional menu"""
    if options:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"    {i}. {option}")
        while True:
            try:
                choice = int(input("Choice: "))
                if 1 <= choice <= len(options):
                    return choice - 1
                print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    else:
        return input(f"{prompt}: ")


def generate_script(prompt, api_key):
    """Call Claude API with prompt"""
    print("\n" + "="*60)
    print("CLAUDE IS WORKING...")
    print("="*60)
    print("- Conducting online research")
    print("- Analyzing sources")
    print("- Generating podcast script")
    print("- Formatting dialogue")
    print("")
    print("This may take 30-60 seconds...")
    print("="*60 + "\n")
    
    client = Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        print("✓ Script generated successfully!\n")
        
        # Track usage
        usage = response.usage
        print(f"[USAGE] Claude - Input: {usage.input_tokens} tokens, Output: {usage.output_tokens} tokens")
        
        return response.content[0].text, usage
    except Exception as e:
        print(f"\n✗ Error calling Claude API: {e}\n")
        return None, None


def revise_script(original_script, revision_guidance, api_key):
    """Request Claude to revise script"""
    prompt = f"""Here is a podcast script:

{original_script}

Please revise this script according to the following guidance:
{revision_guidance}

Provide the complete revised script maintaining the same format with Speaker A and Speaker B labels."""
    
    print("\n" + "="*60)
    print("CLAUDE IS REVISING SCRIPT...")
    print("="*60)
    print("- Analyzing your feedback")
    print("- Updating script content")
    print("- Maintaining dialogue format")
    print("")
    print("This may take 30-60 seconds...")
    print("="*60 + "\n")
    
    return generate_script(prompt, api_key)


def extract_and_save_sources(script, project_name):
    """Extract sources from Claude's response and save separately"""
    sources_pattern = r'(?:^|\n)(?:SOURCES FOUND:|Sources?:)(.*?)(?:\n\n---|\Z)'
    
    match = re.search(sources_pattern, script, re.DOTALL | re.IGNORECASE)
    
    if match:
        sources_content = match.group(1).strip()
        
        sources_file = Path(f"./projects/{project_name}/scripts/{project_name}_sources.txt")
        with open(sources_file, 'w', encoding='utf-8') as f:
            f.write(f"Research Sources for {project_name}\n")
            f.write("="*60 + "\n\n")
            f.write(sources_content)
            f.write("\n\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        print(f"✓ Sources saved to: {sources_file}")
        
        script_clean = re.sub(sources_pattern, '', script, flags=re.DOTALL|re.IGNORECASE)
        return script_clean.strip()
    
    return script


def save_script(script, project_name, draft_number, language_code='EN'):
    """Save script with versioned filename including language code and timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    lang_upper = language_code.upper()
    filename = f"{project_name}_{lang_upper}_{timestamp}_draft{draft_number}.txt"
    path = Path(f"./projects/{project_name}/scripts/{filename}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(script)
    return path


def save_prompt(prompt, project_name, filename):
    """Save prompt to project folder"""
    path = Path(f"./projects/{project_name}/prompts/{filename}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    return path


def clean_script_for_audio(script):
    """Remove non-dialogue content before audio generation
    
    Removes:
    - Claude's meta-commentary preamble
    - Search quality checks
    - Search tags
    - Sources section
    - Markdown formatting
    - Stage directions
    """
    print("\n[INFO] Cleaning script for audio generation...")
    
    original_length = len(script)
    
    # CRITICAL: Remove Claude's meta-commentary at the start
    # Everything before the first "Speaker A:" or "Speaker B:"
    speaker_pattern = r'(?:Speaker [AB]:)'
    match = re.search(speaker_pattern, script)
    if match:
        # Found first speaker label - keep everything from there
        script = script[match.start():]
        print(f"[INFO] Removed Claude's preamble ({match.start()} chars)")
    
    # Remove search quality checks and search tags
    script = re.sub(r'<search_quality_check>.*?</search_quality_check>', '', script, flags=re.DOTALL)
    script = re.sub(r'<search_quality_score>.*?</search_quality_score>', '', script, flags=re.DOTALL)
    script = re.sub(r'<search>.*?</search>', '', script, flags=re.DOTALL)
    
    # Remove "I'll conduct research..." type preambles
    script = re.sub(r"(?:^|\n)I'?ll? (?:conduct|create|generate|search).*?(?=Speaker [AB]:|$)", '', script, flags=re.DOTALL|re.IGNORECASE)
    script = re.sub(r"(?:^|\n)Let me (?:conduct|create|generate|search).*?(?=Speaker [AB]:|$)", '', script, flags=re.DOTALL|re.IGNORECASE)
    script = re.sub(r"(?:^|\n)Now I'?ll? (?:conduct|create|generate).*?(?=Speaker [AB]:|$)", '', script, flags=re.DOTALL|re.IGNORECASE)
    
    # CRITICAL: Remove sources section FIRST - CUT EVERYTHING after "SOURCES FOUND:"
    # This must happen BEFORE removing "---" because there's often a "---" before sources
    print("[DEBUG] Checking for sources section...")
    
    sources_removed = False
    for pattern in [r'\n\s*SOURCES FOUND:', r'\n\s*\*\*SOURCES FOUND:\*\*', r'\n\s*##\s*SOURCES FOUND:']:
        match = re.search(pattern, script, re.IGNORECASE)
        if match:
            before_length = len(script)
            # Cut everything from the match position onwards
            script = script[:match.start()]
            after_length = len(script)
            print(f"[INFO] ✓ CUT SOURCES: Removed {before_length - after_length} chars after 'SOURCES FOUND:'")
            sources_removed = True
            break
    
    if not sources_removed:
        print("[WARNING] No 'SOURCES FOUND:' marker detected - check if script has sources section")
        # Try to find if there are numbered sources like "1. **Source**"
        if re.search(r'\n\d+\.\s+\*\*.*?\*\*', script):
            print("[WARNING] Found numbered sources but no 'SOURCES FOUND:' marker - may include sources in audio!")
    else:
        # Double-check sources are gone
        if re.search(r'\n\d+\.\s+\*\*.*?\*\*', script):
            print("[ERROR] Sources still present after removal! Check script format.")
        else:
            print("[INFO] ✓ Verified: No sources in cleaned script")
    
    # NOW remove "---" separators (often appear before sources section)
    script = re.sub(r'^-{3,}$', '', script, flags=re.MULTILINE)
    print("[DEBUG] Removed separator lines (---)")
    
    # Remove markdown headers
    script = re.sub(r'^#+\s+.*$', '', script, flags=re.MULTILINE)
    
    # Remove stage directions (but NOT audio tags!)
    script = re.sub(r'^\*[^\[]*\*$', '', script, flags=re.MULTILINE)
    
    # Remove word counts
    script = re.sub(r'(?:Total|Approximately)?\s*\d+\s*words?', '', script, flags=re.IGNORECASE)
    script = re.sub(r'Total script length:.*$', '', script, flags=re.MULTILINE|re.IGNORECASE)
    
    # Clean up extra blank lines
    script = re.sub(r'\n{3,}', '\n\n', script)
    script = script.strip()
    
    cleaned_length = len(script)
    removed = original_length - cleaned_length
    
    if removed > 0:
        print(f"[INFO] Removed {removed} characters of non-dialogue content")
    
    return script


def validate_template_quality(script):
    """Check if script uses dynamic features"""
    warnings = []
    
    if '[interrupting]' not in script.lower() and '[overlapping]' not in script.lower():
        warnings.append("⚠ No interruptions found - dialogue may sound too formal")
    
    emotion_tags = ['[excited]', '[curious]', '[skeptical]', '[surprised]', '[thoughtful]']
    if not any(tag.lower() in script.lower() for tag in emotion_tags):
        warnings.append("⚠ No emotional tags found - dialogue may lack energy")
    
    reaction_tags = ['[laughs]', '[chuckles]', '[sighs]', '[gasps]']
    if not any(tag.lower() in script.lower() for tag in reaction_tags):
        warnings.append("⚠ No reaction tags found - may sound robotic")
    
    if re.search(r'\bSie\b', script):
        warnings.append("⚠ Found 'Sie' form - should use informal 'Du' for friendly tone")
    
    if warnings:
        print("\n" + "="*60)
        print("SCRIPT QUALITY WARNINGS")
        print("="*60)
        for warning in warnings:
            print(warning)
        print("")
        print("Consider revising for better audio quality.")
        print("="*60)
        
        proceed = input("\nProceed anyway? (Y/n): ")
        if proceed.lower() == 'n':
            return False
    
    return True


def save_debug_chunk(chunk, chunk_num, project_name):
    """Save chunk content for debugging"""
    debug_dir = Path(f"./projects/{project_name}/debug")
    debug_file = debug_dir / f"chunk_{chunk_num}_content.json"
    
    with open(debug_file, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    
    log_debug(f"Chunk {chunk_num} saved to: {debug_file}")
    return debug_file


def parse_script_to_dialogue(script, voice_ids):
    """Parse script with Speaker A/B labels into ElevenLabs dialogue format
    
    CRITICAL: Preserves [audio tags] in square brackets for ElevenLabs v3
    """
    print("\n[DEBUG] Parsing script into dialogue format...")
    print(f"[DEBUG] Script length: {len(script)} characters")
    
    lines = script.split('\n')
    dialogue = []
    current_speaker = None
    current_text = []
    
    print("[DEBUG] First 10 lines of script:")
    for i, line in enumerate(lines[:10]):
        print(f"  {i}: {line[:80]}")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        is_speaker_a = any(marker in line.lower() for marker in 
                          ['speaker a:', '**speaker a', 'speaker a -'])
        is_speaker_b = any(marker in line.lower() for marker in 
                          ['speaker b:', '**speaker b', 'speaker b -'])
        
        if is_speaker_a:
            if current_text and current_speaker:
                dialogue.append({
                    'voice_id': voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b'],
                    'text': ' '.join(current_text).strip()
                })
                print(f"[DEBUG] Added {current_speaker} segment: {len(' '.join(current_text))} chars")
            
            current_speaker = 'speaker_a'
            # CRITICAL FIX: Don't strip [square brackets] - they're audio tags!
            text = line.split(':', 1)[-1].strip().replace('**', '').strip()
            current_text = [text] if text else []
            
        elif is_speaker_b:
            if current_text and current_speaker:
                dialogue.append({
                    'voice_id': voice_ids['speaker_a' if current_speaker == 'speaker_a' else 'speaker_b'],
                    'text': ' '.join(current_text).strip()
                })
                print(f"[DEBUG] Added {current_speaker} segment: {len(' '.join(current_text))} chars")
            
            current_speaker = 'speaker_b'
            # CRITICAL FIX: Don't strip [square brackets] - they're audio tags!
            text = line.split(':', 1)[-1].strip().replace('**', '').strip()
            current_text = [text] if text else []
            
        elif current_speaker:
            if not line.startswith('#') and not line.startswith('---'):
                current_text.append(line)
    
    if current_text and current_speaker:
        voice_id = voice_ids['speaker_a'] if current_speaker == 'speaker_a' else voice_ids['speaker_b']
        dialogue.append({'voice_id': voice_id, 'text': ' '.join(current_text).strip()})
        print(f"[DEBUG] Added final {current_speaker} segment: {len(' '.join(current_text))} chars")
    
    print(f"[DEBUG] Total dialogue segments: {len(dialogue)}")
    
    if not dialogue:
        print("[ERROR] No dialogue segments found!")
        print("[ERROR] Script may not have proper Speaker A: / Speaker B: labels")
        print("\n[HELP] Script should look like:")
        print("Speaker A: Hello, welcome to the podcast!")
        print("Speaker B: Thanks for having me!")
        return None
    
    return dialogue


def chunk_dialogue(inputs, max_chars=4500):
    """Split dialogue inputs into chunks under character limit"""
    chunks = []
    current_chunk = []
    current_length = 0
    
    for item in inputs:
        item_length = len(item['text'])
        
        if current_length + item_length > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [item]
            current_length = item_length
        else:
            current_chunk.append(item)
            current_length += item_length
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def generate_audio(script, config, language_code, mode='prototype', speed=1.0, project_name=None):
    """Call ElevenLabs Text-to-Dialogue API with enhanced error logging"""
    print(f"\nGenerating audio in {mode.upper()} mode...")
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in environment")
        return None
    
    # Map language codes to config keys for ALL supported languages
    language_map = {
        'de': 'german',
        'en': 'english',
        'nl': 'dutch'
    }
    language = language_map.get(language_code, 'english')
    
    voice_ids = {
        'speaker_a': config['languages'][language]['elevenlabs_voices']['speaker_a_female'],
        'speaker_b': config['languages'][language]['elevenlabs_voices']['speaker_b_male']
    }
    
    print(f"[DEBUG] Language: {language.upper()} ({language_code})")
    print(f"[DEBUG] Using voices: Speaker A = {voice_ids['speaker_a']}, Speaker B = {voice_ids['speaker_b']}")
    
    dialogue = parse_script_to_dialogue(script, voice_ids)
    
    if not dialogue:
        print("\n" + "="*60)
        print("SCRIPT FORMAT ERROR")
        print("="*60)
        print("The script doesn't have proper Speaker A: / Speaker B: labels.")
        print("")
        print("Options to fix:")
        print("1. Go back and ask Claude to revise with proper format")
        print("2. Manually edit the script file to add labels")
        print("3. Use 'Edit script and regenerate' option")
        print("="*60)
        return None
    
    inputs = [{
        "text": seg['text'], 
        "voice_id": seg['voice_id'],
        "voice_settings": {"speed": speed}
    } for seg in dialogue]
    
    total_length = sum(len(item['text']) for item in inputs)
    print(f"[DEBUG] Total dialogue length: {total_length} characters")
    
    if total_length > 5000:
        print(f"[INFO] Content exceeds 5000 character limit, splitting into chunks...")
        chunks = chunk_dialogue(inputs, max_chars=4500)
        print(f"[INFO] Split into {len(chunks)} chunks")
    else:
        chunks = [inputs]
        print(f"[INFO] Content fits in single request")
    
    url = "https://api.elevenlabs.io/v1/text-to-dialogue"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    
    audio_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        chunk_length = sum(len(item['text']) for item in chunk)
        print(f"\n[DEBUG] Chunk {i}/{len(chunks)}: {len(chunk)} segments, {chunk_length} characters")
        
        # Save chunk for debugging
        if project_name:
            debug_file = save_debug_chunk(chunk, i, project_name)
            print(f"[DEBUG] Chunk {i} saved to: {debug_file}")
        
        payload = {"inputs": chunk}
        
        # Retry logic with detailed error messages
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                log_debug(f"Attempt {attempt + 1}/{max_retries} for chunk {i}/{len(chunks)}")
                
                if attempt > 0:
                    print(f"[RETRY] Attempt {attempt + 1}/{max_retries} for chunk {i}/{len(chunks)}...")
                    time.sleep(retry_delay * attempt)
                
                print(f"Sending chunk {i}/{len(chunks)} to ElevenLabs...")
                
                # Make the request with timeout
                log_debug(f"POST {url}")
                log_debug(f"Payload size: {len(json.dumps(payload))} bytes")
                
                response = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
                
                log_debug(f"Response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_body = response.text
                    print(f"\n[ERROR] Status {response.status_code}: {error_body}")
                    
                    # If 500 error, retry
                    if response.status_code == 500 and attempt < max_retries - 1:
                        print(f"[INFO] Server error on attempt {attempt + 1}, retrying in {retry_delay * (attempt + 1)} seconds...")
                        continue
                    
                    # If other error or last attempt, raise
                    response.raise_for_status()
                
                # Success - collect audio
                chunk_audio = b''
                bytes_received = 0
                for data in response.iter_content(chunk_size=8192):
                    if data:
                        chunk_audio += data
                        bytes_received += len(data)
                
                log_debug(f"Received {bytes_received} bytes")
                
                audio_parts.append(chunk_audio)
                print(f"✓ Chunk {i}/{len(chunks)} generated ({len(chunk_audio) / 1024 / 1024:.1f} MB)")
                break  # Success, exit retry loop
                
            except requests.exceptions.Timeout as e:
                print(f"\n[ERROR] Timeout after 120 seconds on chunk {i}")
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying in {retry_delay * (attempt + 1)} seconds...")
                    continue
                else:
                    print(f"\n✗ Failed after {max_retries} attempts: Timeout")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"\n[ERROR] Request exception on chunk {i}: {type(e).__name__}")
                print(f"[ERROR] Details: {str(e)}")
                
                if hasattr(e, 'response') and e.response is not None:
                    print(f"[ERROR] Response body: {e.response.text}")
                
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying in {retry_delay * (attempt + 1)} seconds...")
                    continue
                else:
                    print(f"\n✗ Failed after {max_retries} attempts")
                    print(f"\n[DEBUG] Chunk {i} content saved to:")
                    print(f"  projects/{project_name}/debug/chunk_{i}_content.json")
                    return None
            
            except Exception as e:
                print(f"\n[ERROR] Unexpected exception on chunk {i}: {type(e).__name__}")
                print(f"[ERROR] Details: {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying in {retry_delay * (attempt + 1)} seconds...")
                    continue
                else:
                    return None
    
    # Concatenate all audio chunks
    if len(audio_parts) > 1:
        print(f"\n[INFO] Concatenating {len(audio_parts)} audio chunks...")
        audio_data = b''.join(audio_parts)
    else:
        audio_data = audio_parts[0]
    
    print(f"✓ Complete audio generated ({len(audio_data) / 1024 / 1024:.1f} MB)")
    print(f"[USAGE] ElevenLabs - {total_length} characters processed")
    
    return audio_data, total_length


def read_text_file(filepath):
    """Read plain text file with verbose feedback"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"      [Text file: {len(lines)} lines, {len(content)} chars]")
        return content
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"


def read_docx_file(filepath):
    """Read DOCX file with verbose feedback"""
    if not DOCX_AVAILABLE:
        return "[python-docx not installed - run: pip install python-docx]"
    
    try:
        doc = DocxDocument(filepath)
        num_paragraphs = len(doc.paragraphs)
        print(f"      [DOCX: {num_paragraphs} paragraphs detected]")
        
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        
        print(f"      [Extracted {len(text)} non-empty paragraphs]")
        return '\n'.join(text)
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"


def read_pdf_file(filepath):
    """Read PDF file with verbose feedback"""
    if not PDF_AVAILABLE:
        return "[PyPDF2 not installed - run: pip install PyPDF2]"
    
    try:
        text = []
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            print(f"      [PDF: {num_pages} pages detected]")
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text.append(page_text)
                    print(f"      [Page {page_num}/{num_pages}: {len(page_text)} chars]", end='\r')
            
            print()  # New line after progress
        return '\n'.join(text)
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"


def read_pptx_file(filepath):
    """Read PPTX file with verbose feedback"""
    if not PPTX_AVAILABLE:
        return "[python-pptx not installed - run: pip install python-pptx]"
    
    try:
        prs = Presentation(filepath)
        num_slides = len(prs.slides)
        print(f"      [PPTX: {num_slides} slides detected]")
        
        text = []
        for slide_num, slide in enumerate(prs.slides, 1):
            text.append(f"[Slide {slide_num}]")
            shape_count = 0
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text.append(shape.text)
                    shape_count += 1
            print(f"      [Slide {slide_num}/{num_slides}: {shape_count} text elements]", end='\r')
        
        print()  # New line after progress
        return '\n'.join(text)
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"


def read_source_document(filepath):
    """Read document based on file extension"""
    path = Path(filepath)
    ext = path.suffix.lower()
    
    if ext in ['.txt', '.md']:
        return read_text_file(filepath)
    elif ext == '.docx':
        return read_docx_file(filepath)
    elif ext == '.pdf':
        return read_pdf_file(filepath)
    elif ext == '.pptx':
        return read_pptx_file(filepath)
    else:
        return f"[Unsupported file type: {ext}]"


def list_source_files(project_name):
    """List available source files in project sources folder"""
    sources_path = Path(f"./projects/{project_name}/sources")
    if not sources_path.exists():
        return []
    
    supported_exts = ['.txt', '.md', '.docx', '.pdf', '.pptx']
    files = []
    for ext in supported_exts:
        files.extend(sources_path.glob(f"*{ext}"))
    
    return sorted([f for f in files if f.name not in ['research_context.txt', 'sources_list.txt']])


def process_source_documents(project_name):
    """Check and process source documents before script generation"""
    sources_path = Path(f"./projects/{project_name}/sources")
    sources_path.mkdir(parents=True, exist_ok=True)
    
    while True:
        print("\n" + "="*60)
        print("SOURCE DOCUMENTS CHECK")
        print("="*60)
        
        files = list_source_files(project_name)
        
        if files:
            print(f"Found {len(files)} document(s) in sources folder:")
            for f in files:
                print(f"  - {f.name}")
        else:
            print("No source documents found in sources folder.")
        
        print("\nOptions:")
        print("  1. Proceed (use existing documents if any)")
        print("  2. List current documents")
        print("  3. Add new source files")
        
        choice = input("\nChoice (1-3, default=1): ").strip() or "1"
        
        if choice == "1":
            # Read all documents and return combined text
            if not files:
                print("\n[INFO] No source documents - proceeding with web research only")
                return ""
            
            print("\n[INFO] Reading source documents...")
            combined_text = []
            success_count = 0
            
            for file in files:
                print(f"  Reading: {file.name}...")
                content = read_source_document(file)
                if not content.startswith("[Error") and not content.startswith("["):
                    combined_text.append(f"\n\n### SOURCE: {file.name}\n\n{content}")
                    success_count += 1
                    print(f"    ✓ Successfully read ({len(content)} chars)")
                else:
                    print(f"    ✗ {content}")
            
            print(f"\n[INFO] Successfully read {success_count}/{len(files)} documents")
            return '\n'.join(combined_text) if combined_text else ""
        
        elif choice == "2":
            # List documents (filenames only, no content)
            if not files:
                print("\n[INFO] No documents to list")
                continue
            
            print("\n" + "="*60)
            print("DOCUMENTS IN SOURCES FOLDER")
            print("="*60)
            print(f"\nLocation: {sources_path.absolute()}\n")
            
            for i, file in enumerate(files, 1):
                file_size = file.stat().st_size
                size_kb = file_size / 1024
                print(f"  {i}. {file.name} ({size_kb:.1f} KB)")
            
            print(f"\nTotal: {len(files)} document(s)")
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            # Provide instructions for adding files
            print("\n" + "="*60)
            print("ADD SOURCE DOCUMENTS")
            print("="*60)
            print(f"\nLocation: {sources_path.absolute()}")
            print("\nSupported formats:")
            print("  - Text: .txt, .md")
            print("  - Documents: .docx")
            print("  - PDF: .pdf")
            print("  - Presentations: .pptx")
            print("\nInstructions:")
            print("  1. Copy your files to the sources folder above")
            print("  2. Press Enter when done")
            print("\nNote: Files named 'research_context.txt' and 'sources_list.txt'")
            print("      are reserved and will be ignored.")
            
            input("\nPress Enter when files are ready...")
        
        else:
            print("Invalid choice")


def save_audio(audio_data, project_name, topic, language_code, mode):
    """Save audio file with project name, topic, and language"""
    date = datetime.now().strftime('%Y-%m-%d')
    safe_topic = topic.replace('/', '-').replace('\\', '-')
    filename = f"{project_name}_{safe_topic}_{language_code}_{date}_{mode.upper()}.mp3"
    path = Path(f"./projects/{project_name}/audio/{filename}")
    with open(path, 'wb') as f:
        f.write(audio_data)
    return path


def main():
    """Main pipeline orchestration"""
    print("=== AI Podcast Pipeline v3.0 (Enhanced Debug) ===\n")
    
    if DEBUG_VERBOSE:
        print("[VERBOSE MODE ENABLED - Detailed logging active]\n")
    
    config = load_config()
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY not found in config/.env")
        return
    
    # 1. Project setup
    project_name = get_user_input("Enter project name (alphanumeric, for folders/filenames)").replace(' ', '_').lower()
    topic = get_user_input("Enter podcast topic")
    
    while True:
        try:
            duration = int(get_user_input("Target duration in minutes"))
            if duration > 0:
                break
            print("Duration must be positive")
        except ValueError:
            print("Please enter a valid number")
    
    word_count = duration * 150
    print(f"Calculated word count: ~{word_count} words (150 words/min)")
    
    # 2-4. Style, language, mode selection
    styles = list(config['styles'].keys())
    style_names = [config['styles'][s]['description'] for s in styles]
    style_idx = get_user_input("\nSelect style", style_names)
    selected_style = styles[style_idx]
    
    languages = list(config['languages'].keys())
    language_names = [config['languages'][l]['name'] for l in languages]
    lang_idx = get_user_input("\nSelect language", language_names)
    selected_language = languages[lang_idx]
    language_code = config['languages'][selected_language]['code']
    
    mode_idx = get_user_input("\nSelect mode", [
        "Prototype (lower quality, reduced cost for testing)",
        "Production (full quality)"
    ])
    mode = "prototype" if mode_idx == 0 else "production"
    
    # Get speed setting
    default_speed = config['languages'][selected_language]['speed']
    speed_input = input(f"\nSpeech speed (0.7-1.2, default {default_speed}, Enter to use default): ").strip()
    if speed_input:
        try:
            speed = float(speed_input)
            speed = max(0.7, min(1.2, speed))
            print(f"Using speed: {speed}")
        except ValueError:
            speed = default_speed
            print(f"Invalid, using default: {speed}")
    else:
        speed = default_speed
        print(f"Using default speed: {speed}")
    
    # 5. Create project structure
    print(f"\nCreating project folder: ./projects/{project_name}/")
    project_path = create_project_structure(project_name)
    print(f"  ✓ Created subdirectories")
    
    # 5b. Research context
    research_context_file = project_path / "sources" / "research_context.txt"
    print(f"\n✓ Research context file: {research_context_file}")
    
    # Show what's being used
    default_template = Path("templates/research_contexts/default.txt")
    if default_template.exists() and not (project_path / "sources" / "research_context.txt").exists():
        print("  (Using default template from templates/research_contexts/default.txt)")
    elif (project_path / "sources" / "research_context.txt").exists():
        # Check if it's different from default (i.e., project-specific)
        with open(project_path / "sources" / "research_context.txt", 'r') as f:
            current_content = f.read()
        
        is_customized = "{project_name}" not in current_content  # Simple check
        if is_customized:
            print("  (Using project-specific research context)")
        else:
            print("  (Using default template)")
    
    # Offer choices
    edit_choice = get_user_input("\nResearch context options", [
        "Use as-is (proceed with current context)",
        "Edit current context (customize for this project)",
        "Reset to default template (if you made mistakes)",
        "Show current context"
    ])
    
    if edit_choice == 1:
        print("\nOpening research context in your text editor...")
        subprocess.run([os.environ.get('EDITOR', 'nano'), str(research_context_file)])
        print("✓ Research context updated (now project-specific)")
    elif edit_choice == 2:
        if default_template.exists():
            print("\nResetting to default template...")
            with open(default_template, 'r') as f:
                template_content = f.read()
            with open(research_context_file, 'w') as f:
                f.write(template_content.replace("{project_name}", project_name))
            print("✓ Reset to default template")
        else:
            print("⚠ No default template found at templates/research_contexts/default.txt")
    elif edit_choice == 3:
        print("\n" + "="*60)
        with open(research_context_file, 'r') as f:
            print(f.read())
        print("="*60)
        input("\nPress Enter to continue...")
    
    with open(research_context_file, 'r', encoding='utf-8') as f:
        research_context = f.read()
    
    # 6. Prompt handling
    variables = {
        'duration': duration,
        'word_count': word_count,
        'topic': topic,
        'project_name': project_name
    }
    
    prompt_choice = get_user_input("\nPrompt template options", [
        f"Use default template ({selected_style} / {selected_language})",
        "Load existing template from this project's prompts folder",
        "Copy template from templates folder to project and customize",
        "Edit the chosen template before generating",
        "Start with blank prompt"
    ])
    
    if prompt_choice == 0:
        # Use default template
        template_file = config['styles'][selected_style]['default_template_file']
        template_file = template_file.replace('{language}', selected_language)
        if Path(template_file).exists():
            prompt = load_template(template_file, variables)
        else:
            print(f"WARNING: Template {template_file} not found")
            prompt = f"Create a {duration}-minute podcast script about '{topic}'."
            
    elif prompt_choice == 1:
        # Load existing from project
        project_prompts = list(Path(f"./projects/{project_name}/prompts/").glob("*.txt"))
        if project_prompts:
            prompt_names = [p.name for p in project_prompts]
            prompt_idx = get_user_input("Select prompt file", prompt_names)
            prompt = load_template(project_prompts[prompt_idx], variables)
        else:
            print("No saved prompts found in project")
            prompt = f"Create a {duration}-minute podcast script about '{topic}'."
            
    elif prompt_choice == 2:
        # Copy global template to project
        templates = list(Path("./templates/").glob("*.txt"))
        if templates:
            template_names = [t.name for t in templates]
            template_idx = get_user_input("Select template to copy", template_names)
            prompt = load_template(templates[template_idx], variables)
            save_prompt(prompt, project_name, "copied_template.txt")
            print(f"Template copied to project")
        else:
            prompt = f"Create a {duration}-minute podcast script about '{topic}'."
            
    elif prompt_choice == 3:
        # Edit template before generating
        template_file = config['styles'][selected_style]['default_template_file']
        template_file = template_file.replace('{language}', selected_language)
        if Path(template_file).exists():
            prompt = load_template(template_file, variables)
        else:
            prompt = f"Create a {duration}-minute podcast script about '{topic}'."
        
        save_prompt(prompt, project_name, "edited_prompt.txt")
        prompt_file = Path(f"./projects/{project_name}/prompts/edited_prompt.txt")
        print(f"\nOpening {prompt_file} for editing...")
        subprocess.run([os.environ.get('EDITOR', 'nano'), str(prompt_file)])
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
            
    else:
        # Start with blank
        prompt = f"Create a {duration}-minute podcast script about '{topic}'."
        save_prompt(prompt, project_name, "blank_prompt.txt")
        prompt_file = Path(f"./projects/{project_name}/prompts/blank_prompt.txt")
        subprocess.run([os.environ.get('EDITOR', 'nano'), str(prompt_file)])
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
    
    prompt = f"""{prompt}

=== RESEARCH CONTEXT AND INSTRUCTIONS ===

{research_context}

IMPORTANT: Follow the research instructions above. Conduct thorough online research using web search. Find and analyze the specified number of sources. Document your sources at the end of the script."""
    
    # 7a. Check and process source documents BEFORE prompt review
    source_documents = process_source_documents(project_name)
    if source_documents:
        prompt = f"""{prompt}

=== USER-PROVIDED SOURCE DOCUMENTS ===

The following documents were provided by the user. Reference and cite them where relevant alongside your web research:

{source_documents}

===================================
"""
        print(f"\n[INFO] Added {len(source_documents)} characters from source documents to prompt")
    
    # 7b. Review final prompt (including source documents if added)
    print("\n" + "="*60)
    print("PROMPT REVIEW")
    print("="*60)
    print(f"Topic: {topic}")
    print(f"Duration: {duration} minutes (~{word_count} words)")
    print(f"Style: {config['style_templates'][template_key]['title']}")
    print(f"Language: {config['languages'][selected_language]['name']}")
    if source_documents:
        doc_count = len([s for s in source_documents.split('### SOURCE:') if s.strip()])
        print(f"Source Documents: {doc_count} document(s) attached")
    else:
        print(f"Source Documents: None (web research only)")
    print("="*60)
    print("\nFull prompt saved for your review if needed.")
    print(f"Location: {Path(f'./projects/{project_name}/prompts/temp_prompt.txt').absolute()}")
    print("="*60)
    
    temp_prompt_path = Path(f"./projects/{project_name}/prompts/temp_prompt.txt")
    save_prompt(prompt, project_name, "temp_prompt.txt")
    
    confirm = get_user_input("\nOptions", [
        "Confirm and send to Claude",
        "Edit prompt in text editor",
        "Cancel"
    ])
    
    if confirm == 1:
        print(f"\nOpening prompt in your text editor...")
        subprocess.run([os.environ.get('EDITOR', 'nano'), str(temp_prompt_path)])
        with open(temp_prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        print("✓ Prompt updated")
    elif confirm == 2:
        print("Cancelled")
        return
    
    # 8. Generate script
    script, claude_usage = generate_script(prompt, anthropic_key)
    if not script:
        print("Failed to generate script")
        return
    
    script = extract_and_save_sources(script, project_name)
    
    draft_num = 1
    script_path = save_script(script, project_name, draft_num, language_code)
    print(f"Script generated! ({len(script.split())} words)")
    print(f"Saved to: {script_path}")
    
    # 9. Review and revision loop
    while True:
        print("\n" + "="*60)
        print("SCRIPT REVIEW")
        print("="*60)
        print(f"Script location: {script_path}")
        print("="*60)
        
        action = get_user_input("\nWhat would you like to do?", [
            "Open script in text editor to review",
            "Approve script and proceed to audio",
            "Ask Claude to revise (provide guidance)",
            "Edit script file manually, then regenerate from edits",
            "Save prompt variant to project",
            "Cancel"
        ])
        
        if action == 0:
            print(f"\nOpening {script_path} in your text editor...")
            subprocess.run([os.environ.get('EDITOR', 'nano'), str(script_path)])
            print("\n✓ Editor closed")
            
        elif action == 1:
            if not validate_template_quality(script):
                continue
            break
            
        elif action == 2:
            print("\nProvide specific guidance for what to change.")
            print("Examples:")
            print("  - Add more interruptions and overlapping dialogue")
            print("  - Make it more casual - use 'Du' form and colloquialisms")
            print("  - Add more emotional reactions ([excited], [laughs], etc.)")
            guidance = input("\nRevision guidance: ")
            
            if not guidance.strip():
                print("No guidance provided, skipping revision")
                continue
                
            revised = revise_script(script, guidance, anthropic_key)
            if revised:
                script = extract_and_save_sources(revised, project_name)
                draft_num += 1
                script_path = save_script(script, project_name, draft_num, language_code)
                print(f"✓ Revised script saved to: {script_path}")
            else:
                print("✗ Revision failed")
                
        elif action == 3:
            print(f"\n1. Edit {script_path} in your text editor")
            print("2. Save your changes")
            print("3. Come back here and we'll regenerate with Claude")
            input("\nPress Enter when you're ready to regenerate...")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                edited_script = f.read()
            
            print("\nWhat changes did you make? (This helps Claude understand context)")
            context = input("Your changes: ")
            
            regenerate_prompt = f"""I have a podcast script that was manually edited. Please review it and generate an improved version that:
1. Maintains the edits and improvements that were made
2. Ensures consistent dialogue format with Speaker A: and Speaker B: labels
3. Improves any rough transitions or formatting issues
4. Keeps the same overall structure and content

User's notes on their edits: {context}

Here is the edited script:

{edited_script}

Please provide the improved script maintaining all manual edits and improvements."""
            
            regenerated = generate_script(regenerate_prompt, anthropic_key)
            if regenerated:
                script = extract_and_save_sources(regenerated, project_name)
                draft_num += 1
                script_path = save_script(script, project_name, draft_num, language_code)
                print(f"✓ Regenerated script saved to: {script_path}")
            else:
                print("✗ Regeneration failed")
                
        elif action == 4:
            filename = input("Enter filename for prompt variant: ")
            if not filename.endswith('.txt'):
                filename += '.txt'
            save_prompt(prompt, project_name, filename)
            print(f"✓ Prompt saved to: ./projects/{project_name}/prompts/{filename}")
            
        else:
            print("Cancelled")
            return
    
    # 10. Generate audio
    print("\n" + "="*60)
    print(f"AUDIO GENERATION - {mode.upper()} MODE")
    print("="*60)
    settings = config['elevenlabs_settings'][mode]
    print(f"Quality: {settings['quality']}")
    if settings.get('downsample_enabled'):
        print(f"Bitrate: {settings['downsample_bitrate']} (downsampled)")
    print("\n[INFO] Enhanced error logging enabled")
    print("[INFO] Debug chunks will be saved to: projects/{}/debug/".format(project_name))
    print("="*60)
    
    confirm = input("\nProceed with audio generation? (Y/n): ")
    if confirm.lower() == 'n':
        print("Cancelled")
        return
    
    script_for_audio = clean_script_for_audio(script)
    
    # FINAL SAFETY CHECK - Guarantee sources not in audio
    print("\n[FINAL CHECK] Verifying cleaned script...")
    if 'SOURCES FOUND' in script_for_audio.upper():
        print("[ERROR] ❌ SOURCES STILL IN SCRIPT!")
        print("Attempting emergency removal...")
        # Emergency fallback - find any variant and cut
        idx = script_for_audio.upper().find('SOURCES FOUND')
        if idx > 0:
            script_for_audio = script_for_audio[:idx]
            print(f"[INFO] Emergency cut at position {idx}")
    
    if re.search(r'\n\d+\.\s+\*\*', script_for_audio):
        print("[WARNING] ⚠️ Numbered list detected - may be sources!")
        print("First 200 chars of end of script:")
        print(script_for_audio[-200:])
        print("\nLast 50 chars:")
        print(repr(script_for_audio[-50:]))
        confirm = input("\nSources may be in audio. Continue anyway? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted - fix script manually")
            return
    else:
        print("[INFO] ✓ Verified clean - no sources detected")
    
    audio_data, elevenlabs_chars = generate_audio(script_for_audio, config, language_code, mode, speed, project_name)
    if not audio_data:
        print("\n" + "="*60)
        print("AUDIO GENERATION FAILED")
        print("="*60)
        print("Debug information saved to:")
        print(f"  projects/{project_name}/debug/chunk_*_content.json")
        print("\nCheck the debug output above for:")
        print("  - Error type (Timeout, 500, etc.)")
        print("  - Which chunk failed")
        print("  - Response body details")
        print("\nNext steps:")
        print("1. Review the error message")
        print("2. Check failed chunk JSON")
        print("3. Try running again (may be temporary)")
        print("="*60)
        return
    
    audio_path = save_audio(audio_data, project_name, topic, language_code, mode)
    
    # 11. Display results
    print("\n" + "="*60)
    print("✓ PODCAST GENERATED SUCCESSFULLY!")
    print("="*60)
    print(f"File: {audio_path}")
    print(f"Size: {len(audio_data) / 1024 / 1024:.1f} MB")
    print(f"Mode: {mode.upper()}")
    print("="*60)
    print("USAGE SUMMARY:")
    print(f"  Claude API:")
    print(f"    - Input tokens: {claude_usage.input_tokens:,}")
    print(f"    - Output tokens: {claude_usage.output_tokens:,}")
    print(f"    - Total tokens: {claude_usage.input_tokens + claude_usage.output_tokens:,}")
    print(f"  ElevenLabs API:")
    print(f"    - Characters: {elevenlabs_chars:,}")
    print("="*60)
    
    # 12. Save prompt
    save = input("\nSave final prompt to project? (Y/n): ")
    if save.lower() != 'n':
        filename = input("Enter filename: ")
        if not filename.endswith('.txt'):
            filename += '.txt'
        save_prompt(prompt, project_name, filename)
        print(f"Prompt saved to: ./projects/{project_name}/prompts/{filename}")
    
    # 13. Project summary
    print("\n" + "="*60)
    print("PROJECT SUMMARY")
    print("="*60)
    print(f"Project: {project_name}")
    print(f"Location: ./projects/{project_name}/")
    
    script_count = len(list(Path(f"./projects/{project_name}/scripts/").glob("*draft*.txt")))
    audio_count = len(list(Path(f"./projects/{project_name}/audio/").glob("*.mp3")))
    prompt_count = len(list(Path(f"./projects/{project_name}/prompts/").glob("*.txt")))
    
    print(f"- Scripts: {script_count} drafts")
    print(f"- Audio: {audio_count} files")
    print(f"- Prompts: {prompt_count} files")
    print("="*60)
    
    # 14. Generate another?
    another = input("\nGenerate another podcast? (Y/n): ")
    if another.lower() != 'n':
        print("\n" + "="*60 + "\n")
        main()
    else:
        print("\nPipeline complete!")


if __name__ == "__main__":
    main()
