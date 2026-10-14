from fastapi import HTTPException

from src.services.utils import _format_text_filename
from src.services.modes.story.subjects_creation import generate_subjects_with_mistralai
from src.services.modes.story.text import generate_story_with_openai_jinja, generate_story_with_mistralai
from src.services.modes.story.tts import openai_tts, elevenlabs_text_to_speech, mistral_tts
from src.config.settings import env_settings, FIELDS_DIR, LOCAL_TRACKS_DIR
from src.services.storage import StorageBackend, make_combo_id

storage = StorageBackend(use_bucket=env_settings.use_bucket, settings=env_settings)

def build_story(subject: str, approach: str = "dual_coding", audience: str = "grown-ups", length: str = "long") -> dict:
    # the goal of this function is to call the generation functions, group their respective outputs (text files, audio files),
    # store them for later use and send their data and urls to the frontend.
    story_filename = _format_text_filename(subject)
    story_foldername = _format_text_filename(subject)
    combo_id = make_combo_id(approach, audience, length)
    # story_foldername = subject
    # story_filename = subject
    
    print(subject, approach, audience, length)
    print(story_filename, story_foldername)

    story_title, tagged_story_for_tts, story = generate_story_with_mistralai(subject, temperature=0.2, length=length, approach=approach, audience=audience) # returns text files
    # print(f"Generated story: {story}")
    speech_filename, speech_audio = openai_tts(tagged_story_for_tts, subject) # one text file, one bytes file (mp3)
    # speech_filename, speech_audio = mistral_tts(tagged_story_for_tts, subject) # one text file, one bytes file (mp3)
    # speech_filename, speech_audio = elevenlabs_text_to_speech(tagged_story_for_tts, subject) # one text file, one bytes file (mp3)
    print(f"Generated speech filename: {speech_filename}")
    
    # store files and get their paths
    json_story_filepath = storage.save_txt_to_json_file(story_foldername, story_filename, combo_id, story_title, tagged_story_for_tts, story) # store the story parameters on the server and returns the clean story file
    # print(f"Saved story JSON filepath: {json_story_filepath}")
    speech_filepath = storage.save_mp3_speech_file(story_foldername, combo_id, speech_filename, speech_audio) # store the speech audio file and returns its path
    print(f"Saved speech path: {speech_filepath}")
    
    # get the path for a random local ambient track
    track_url = storage.get_random_track_url(LOCAL_TRACKS_DIR) # returns the path of local ambient track
    track_title = track_url.replace(".mp3", "").replace("_", " ").title() if track_url else None
    print(f"Selected track title: {track_title}")
    
    # Get audio urls for the payload:
    speech_url = storage.get_speech_url(story_filename, combo_id) 
    print(f"Speech URL: {speech_url}, Track URL: {track_url}")
    
    frontend_payload = {
        "storyFilename": story_filename,
        "storyTitle": story_title,
        "story": story,
        "speechUrl": speech_url,
        "trackUrl": track_url,
        "trackTitle": track_title
    }
    
    return frontend_payload

def load_story(subject: str, approach: str, audience: str, length: str, regenerate_mp3: bool) -> dict:
    # Load an existing story from stored JSON and speech files
    try:
        print(f"Loading story: {subject}")
        story_filename = _format_text_filename(subject)
        story_foldername = _format_text_filename(subject)
        combo_id = make_combo_id(approach, audience, length)
        story_title = storage.get_text_title_from_json_file(story_filename, combo_id)
        print(f"Story filename: {story_filename}, Story title: {story_title}")

        story = storage.get_clean_text_from_json_file(story_filename, combo_id)
        tagged_story_for_tts = storage.get_tagged_text_from_json_file(story_filename, combo_id)  # Add this helper if needed

        # Check if MP3 exists; regenerate if missing and flag is True
        speech_url = storage.get_speech_url(story_filename, combo_id)
        
        if regenerate_mp3 and not speech_url:
            print(f"MP3 missing for {story_filename}. Regenerating...")
            speech_filename, speech_audio = openai_tts(tagged_story_for_tts, subject)  # Your TTS function
            # speech_filename, speech_audio = mistralai_tts(tagged_story_for_tts, subject)  # Your TTS function
            speech_url = storage.save_mp3_speech_file(story_foldername, combo_id, speech_filename, speech_audio)
            
        # URLs only (no filesystem paths)
        track_url = storage.get_random_track_url(LOCAL_TRACKS_DIR)
        track_filename = track_url.split('/')[-1] if track_url else None
        track_title = track_filename.replace(".mp3", "").replace("_", " ").title() if track_filename else None

        # Frontend payload (camelCase aliases handled by StoryResponse)
        frontend_payload = {
            "storyFilename": story_filename,
            "storyTitle": story_title,
            "story": story,
            "speechUrl": speech_url,
            "trackUrl": track_url,
            "trackTitle": track_title
        }

        return frontend_payload

    except Exception as e:
        print(f"Error loading story: {e}")
        raise HTTPException(status_code=500, detail=str(e))
