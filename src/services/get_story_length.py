from src.data.fetch_spotify_duration import fetch_spotify_duration
from src.data.fetch_youtube_duration import fetch_youtube_duration

def get_user_story_length(user_length: int, wpm: int = 178) -> int:
    words = (wpm * user_length)
    estimated_chars = words * 5
    return estimated_chars

def get_spotify_story_length(track_duration: int, wpm: int = 178) -> int:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    words = (wpm / 60) * track_duration  # Words based on WPM and duration
    story_length = words * 5  # Approximate story_length (average word length)
    return int(story_length)

def get_youtube_story_length(track_duration: int, wpm: int = 178) -> int:
    youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
    words = (wpm / 60) * track_duration  # Words based on WPM and duration
    story_length = words * 5  # Approximate story_length (average word length)
    return int(story_length)
