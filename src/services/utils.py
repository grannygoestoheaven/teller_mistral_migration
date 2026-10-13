import re

# helper functions for parameters, track selection, and story generation
def _prepare_story_parameters(request_form):
    return subject

def _find_story_id_by_filename(filename: str, manifest: dict) -> str:
    """Find the story ID in the manifest based on the filename."""
    title_to_id_dict = {v['title']: k for k, v in manifest.items()}
    story_id = title_to_id_dict[filename]
    return story_id

def _format_text_filename(subject: str) -> str:
    """Generate a text filename with underscores from a raw subject"""
    return re.sub(r'[^\w\-_]', '_', subject.strip().lower())

# def _format_text_filename(subject: str, pace: bool) -> str:
#     """Generate a text filename with underscores from a raw subject"""
#     return re.sub(r'[^\w\-_]', '_', subject.strip().lower()) if not pace else re.sub(r'[^\w\-_]', '_', subject.strip().lower()) + "_pace"

def _format_mp3_filename(subject: str, max_length: int = 200) -> str:
    """Generate an mp3 filename with underscores from a raw subject."""
    if not subject or not isinstance(subject, str):
        return "mistral_story.mp3"
        
    mp3_filename = re.sub(r'[^\w\-_]', '_', subject.strip().lower())
    
    # Ensure .mp3 extension
    if not mp3_filename.endswith(".mp3"):
        mp3_filename += ".mp3"

    # Handle edge cases
    if len(mp3_filename) > max_length:
        mp3_filename = mp3_filename[:max_length - 4] + ".mp3"
    if mp3_filename == ".mp3":
        return "mistral_story.mp3"
        
    return mp3_filename

# def _format_mp3_filename(subject: str, pace: bool, max_length: int = 200) -> str:
#     """Generate an mp3 filename with underscores from a raw subject."""
#     if not subject or not isinstance(subject, str):
#         return "mistral_story.mp3"
        
#     mp3_filename = re.sub(r'[^\w\-_]', '_', subject.strip().lower()) if not pace else re.sub(r'[^\w\-_]', '_', subject.strip().lower()) + "_pace"
    
#     # Ensure .mp3 extension
#     if not mp3_filename.endswith(".mp3"):
#         mp3_filename += ".mp3"

#     # Handle edge cases
#     if len(mp3_filename) > max_length:
#         mp3_filename = mp3_filename[:max_length - 4] + ".mp3"
#     if mp3_filename == ".mp3":
#         return "mistral_story.mp3"
        
#     return mp3_filename

# def _clean_story_text(story: str) -> str:
#     """
#     Clean generated story text to enforce:
#     1. Proper sentence boundaries before <[silence:1200]>
#     2. No Markdown (*italics*)
#     3. No fragments with tags
#     4. Normalized whitespace/punctuation
#     """
#     if not story:
#         return story

#     # Step 1: Remove Markdown (e.g., *italics*)
#     cleaned = re.sub(r'\*(.*?)\*', r'\1', story)  # Replace *text* with text

#     # Step 2: Fix fragments before tags (add period if missing)
#     cleaned = re.sub(r'([^.!?])\s*<\[silence:\d+]>', r'\1. ', cleaned)  # Add period before tag if needed

#     # Step 3: Ensure tags follow proper punctuation (keep existing correct tags)
#     cleaned = re.sub(r'([.!?])\s*<\[silence:\d+]>', r'\1<[silence:1200]>', cleaned)

#     # Step 4: Split clauses into sentences (e.g., after em dashes/parentheses)
#     cleaned = re.sub(r'([a-z])\s*([—\(])', r'\1. \2', cleaned, flags=re.IGNORECASE)

#     # Step 5: Normalize whitespace and punctuation
#     cleaned = re.sub(r'\s+', ' ', cleaned)  # Collapse multiple spaces
#     cleaned = re.sub(r'\.([A-Z])', r'. \1', cleaned)  # Space after periods
#     cleaned = re.sub(r'\.\.+', '.', cleaned)  # Fix multiple periods

#     # Step 6: Remove orphaned tags (no preceding punctuation)
#     cleaned = re.sub(r'([^.!?])\s*<\[silence:\d+]>', r'\1', cleaned)

#     return cleaned.strip()

def _clean_story_text(story: str) -> str:
    """
    Clean the story text by removing <[silence]> tags and ensuring proper punctuation. The goal is to have
    a well-formed story with sentences ending in periods, and to remove unnecessary whitespace.
    """
    if not story:
        return story
    # cleaned = re.sub(r'<\[silence:1200]>(\s*)', story)
    cleaned = re.sub(r'<\[silence:1200]>(\s*)', lambda m: ' ' if m.group(1) else '', story)
    cleaned = re.sub(r'([a-z])(\s*\n|$)', r'\1.\2', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\.\.+', '.', cleaned)
    cleaned = re.sub(r'\.([^ \n])', r'. \1', cleaned)
    return cleaned.strip()

def _remove_silence_tags(story: str) -> str:
    """Remove <[silence:ms]> tags from the story text."""
    if not story:
        return story
    # cleaned = re.sub(r'<\[silence:\d+\]>', '', story).strip()
    # cleaned = re.sub(r'<\[silence:\d+ms\]>', '', story).strip()
    # Match <[silence:1200ms], <[silence:1200], <silence:1200>, etc.
    cleaned = re.sub(r'<\[?silence:\d+ms?\]?>', '', story).strip()
    # cleaned = re.sub(r'\.([^ \n])', r'. \1', cleaned)
    cleaned = re.sub(r'\.([^ \n])', r'. \1', cleaned)
    return cleaned.strip()

# def _clean_story_text(tts_text: str) -> str:
#     """
#     Cleans TTS-tagged text for display by:
#     1. Removing all <[silence:1200]> tags.
#     2. Normalizing whitespace (collapsing multiple spaces/newlines).
#     3. Ensuring punctuation is properly spaced (e.g., "word ." → "word.").
#     4. Trimming leading/trailing whitespace.
#     """
#     # Step 1: Remove TTS tags and asterisks
#     cleaned = re.sub(r'<\[silence:\d+\]>', '', tts_text)
#     cleaned = re.sub(r'\*', '', cleaned)
    
#     # Step 2: Normalize whitespace and punctuation
#     cleaned = re.sub(r'\s+', ' ', cleaned)  # Collapse all whitespace to single space
#     cleaned = re.sub(r'\s+([?.!,;])', r'\1', cleaned)  # Remove space before punctuation
#     cleaned = re.sub(r'([?.!,;])(\w)', r'\1 \2', cleaned)  # Add space after punctuation if missing
#     cleaned = cleaned.strip()

#     # Step 3: Ensure sentences start with a capital letter after tags
#     cleaned = re.sub(r'(^|\.\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(), cleaned)

#     return cleaned

# def _clean_story_text(story: str) -> str:
#     if not story:
#         return story
#     cleaned = re.sub(r'<\[silence]>\s*', ' ', story)  # Remove silence tags
#     cleaned = re.sub(r'[\n\\n]+', ' ', cleaned)       # Remove all newlines (actual or escaped)
#     cleaned = re.sub(r'\s+', ' ', cleaned)            # Collapse all whitespace
#     cleaned = re.sub(r'\.\s*([A-Z])', r'. \1', cleaned)  # Fix spacing after periods
    
#     return cleaned.strip()                            # Trim leading/trailing spaces

def _clean_story_title(subject: str) -> str:
    """Generate a clean story filename with spaces from an underscored filename."""
    if not subject or not isinstance(subject, str):
        return "Mistral Story"
    
    return subject.replace("_", " ").title()

# def _clean_story_title_pace(subject: str) -> str:
#     """Generate a clean story filename with 'pace' appended at the end"""
#     if not subject or not isinstance(subject, str):
#         return "Mistral Story"
    
#     return subject.replace("_", " ").title() + "_pace"
