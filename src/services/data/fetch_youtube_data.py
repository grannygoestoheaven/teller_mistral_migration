from youtube_transcript_api import YouTubeTranscriptApi

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# import isodate

def get_youtube_transcript():
    # Get the raw transcript
    transcript_list = YouTubeTranscriptApi.get_transcript('VIDEO_ID')
    # Combine the transcript pieces into a single string
    full_transcript = " ".join([item['text'] for item in transcript_list])
    
def _get_ambient_landscapes_from_youtube(base_dir, logger):
    youtube_dir = os.path.join(base_dir, 'static', 'audio', YOUTUBE_AMBIENT_LANDSCAPES_DIR)
    os.makedirs(youtube_dir, exist_ok=True)
    try:
        url_files = [f for f in os.listdir(youtube_dir) if f.endswith('.txt')]
        if not url_files:
            logger.warning(f"No URL files found in {youtube_dir}")
            return None
        url_file = random.choice(url_files)
        url_file_path = os.path.join(youtube_dir, url_file)
        urls = _read_youtube_urls(url_file_path, logger)
        if not urls:
            logger.warning(f"No valid URLs found in {url_file}")
            return None
        return random.choice(urls)
    except FileNotFoundError:
        logger.error(f"Ambient landscapes directory not found: {youtube_dir}")
        return None

# The following YouTube functions are currently unused and can be kept for future expansion or removed.
def _read_youtube_urls(file_path, logger):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f 
                    if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        logger.error(f"Error reading YouTube URLs from {file_path}: {str(e)}")
        return []

def get_youtube_client(api_key: str):
    return build('youtube', 'v3', developerKey=api_key)
