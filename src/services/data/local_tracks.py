import random

class AmbientTrackManager:
    _instance = None
    _tracks = []
    _played_tracks = []
    _initialized = False

    @classmethod
    def initialize(cls, tracks_dir: str) -> None:
        if cls._initialized:
            return
        try:
            cls._tracks = [
                f.name for f in tracks_dir.iterdir()
                if f.suffix.lower() in (".mp3", ".wav", ".flac")
            ]
            random.shuffle(cls._tracks)
        except FileNotFoundError:
            cls._tracks = []
        cls._initialized = True

    @classmethod
    def get_next_track(cls, tracks_dir) -> str | None:  # Remove base_dir argument
        if not cls._initialized:
            cls.initialize(tracks_dir)
        if not cls._tracks and not cls._played_tracks:
            return None
        if not cls._tracks:
            cls._tracks, cls._played_tracks = cls._played_tracks, []
            random.shuffle(cls._tracks)

        track_filename = cls._tracks.pop(0)
        cls._played_tracks.append(track_filename)
        
        return str(tracks_dir / track_filename)  # Use LOCAL_TRACKS_DIR directly

def get_random_track_path(tracks_dir) -> str | None:
    """
    Returns the relative path of the next ambient track (e.g., "audio/ambient/track.mp3").
    Returns None if no tracks are available.
    """
    try:
        return AmbientTrackManager.get_next_track(tracks_dir)
    except Exception as e:
        print(f"Error getting ambient track: {e}")  # Replace with your logger
        return None
