from fastapi import HTTPException

from src.services.modes.news.text import generate_news_with_openai, generate_news_with_mistralai
from src.services.modes.story.tts import openai_tts
from src.services.storage import save_txt_to_json_file, save_mp3_speech_file, get_clean_text_from_json_file, get_tagged_text_from_json_file, get_text_title_from_json_file, get_speech_url, get_random_track_url

from src.config.settings import GENERATED_NEWS_DIR, LOCAL_TRACKS_DIR

def build_news(subject: str, narrative_style: str, difficulty: str) -> dict:
    print(subject)
    # the goal of this function is to call the generation functions, group their respective outputs (text files, audio files),
    # store them for later use and send their data and urls to the frontend.
    news_foldername = subject
    news_filename = subject
    
    print (subject, narrative_style, difficulty)
    
    news_title, tagged_news_for_tts, news = generate_news_with_mistral(subject, narrative_style, difficulty) # returns text files
    speech_filename, speech_audio = openai_tts(tagged_news_for_tts, subject) # one text file, one bytes file (mp3)
    print(f"Generated speech filename: {speech_filename}")
    
    # store files and get their paths
    json_news_filepath = save_txt_to_json_file(news_filename, news_title, tagged_news_for_tts, news, GENERATED_NEWS_DIR) # store the news parameters on the server and returns the clean news file
    print(f"Saved news JSON filepath: {json_news_filepath}")
    speech_filepath = save_mp3_speech_file(news_foldername, speech_filename, speech_audio, GENERATED_NEWS_DIR) # store the speech audio file and returns its path
    print(f"Saved speech path: {speech_filepath}")
    
    # get the path for a random local ambient track
    track_filepath = get_random_track_url(LOCAL_TRACKS_DIR) # returns the path of local ambient track
    track_filename = track_filepath.split('/')[-1] if track_filepath else None # get only the filename; last part of the path
    track_title = track_filename.replace(".mp3", "").replace("_", " ").title() if track_filename else None
    print(f"Selected track title: {track_title}")
    
    # Get audio urls for the payload:
    speech_url = f"/static/news/{news_foldername}/{speech_filename}"
    track_url = f"/static/audio/local_ambient_tracks/{track_filename}"
    print(f"Speech URL: {speech_url}, Track URL: {track_url}")
    
    frontend_payload = {
        "newsFilename": news_filename,
        "newsTitle": news_title,
        "news": news,
        "speechUrl": speech_url,
        "trackUrl": track_url,
        "trackTitle": track_title
    }
    
    print(f"Payload constructed: {frontend_payload}")
    
    return frontend_payload

def load_news(subject: str, regenerate_mp3: bool) -> dict:
    # Load an existing news from stored JSON and speech files
    try:
        print(f"Loading news: {subject}")
        news_filename = subject
        news_foldername = subject
        news_title = get_text_title_from_json_file(news_filename)
        print(f"news filename: {news_filename}, news title: {news_title}")

        news = get_clean_text_from_json_file(news_filename)
        tagged_news_for_tts = get_tagged_news_from_json_file(news_filename)  # Add this helper if needed

        # Check if MP3 exists; regenerate if missing and flag is True
        mp3_path = GENERATED_NEWS_DIR / news_foldername / f"{news_filename}.mp3"
        if regenerate_mp3 and not mp3_path.exists():
            print(f"MP3 missing for {news_filename}. Regenerating...")
            speech_filename, speech_audio = openai_tts(tagged_news_for_tts, subject)  # Your TTS function
            save_mp3_speech_file(news_foldername, speech_filename, speech_audio, GENERATED_NEWS_DIR)

        # URLs only (no filesystem paths)
        speech_url = f"/static/NEWS/{news_filename}/{news_filename}.mp3"

        track_path = get_random_track_url(LOCAL_TRACKS_DIR)
        track_filename = track_path.split('/')[-1] if track_path else None
        track_url = f"/static/audio/local_ambient_tracks/{track_filename}"
        track_title = track_filename.replace(".mp3", "").replace("_", " ").title() if track_filename else None

        # Frontend payload (camelCase aliases handled by newsResponse)
        frontend_payload = {
            "newsFilename": news_filename,
            "newsTitle": news_title,
            "news": news,
            "speechUrl": speech_url,
            "trackUrl": track_url,
            "trackTitle": track_title
        }

        print(f"Payload constructed: {frontend_payload}")
        return frontend_payload

    except Exception as e:
        print(f"Error loading news: {e}")
        raise HTTPException(status_code=500, detail=str(e))
