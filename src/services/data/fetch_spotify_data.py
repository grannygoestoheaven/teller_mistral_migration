import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException  # Specific error for API issues

def extract_service_name(track_url: str) -> str:
    if "spotify.com" in track_url:
        return "spotify"
    elif "youtube.com" in track_url:
        return "youtube"
    else:
        return "unknown"

def get_track_duration(track_url: str, client_id: str, client_secret: str, api_key: str) -> int:
    service = extract_service_name(track_url)

    if service == "spotify":
        return fetch_spotify_duration(track_url, client_id, client_secret)
    elif service == "youtube":
        return fetch_youtube_duration(track_url, api_key)
    else:
        print("Unsupported URL format.")
        return None  # Return None instead of raising an error


def fetch_spotify_duration(track_url: str, client_id: str, client_secret: str) -> int:
    """
    Get the duration of a Spotify track in seconds.
    """
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        ))

        track_id = track_url.split('/')[-1].split('?')[0]
        track = sp.track(track_id)  # Correct method to fetch track details

        # Handle missing or unexpected data
        duration_ms = track.get('duration_ms')  # Safely access the duration
        if not duration_ms:
            print("Track duration not found in response.")
            return None

        return duration_ms // 1000  # Return duration in seconds

    except Exception as e:
        print(f"Error fetching Spotify duration: {e}")
        return None

    except SpotifyException as e:
        print(f"Spotify API error: {e}")
    except IndexError:
        print("Invalid Spotify URL format.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
