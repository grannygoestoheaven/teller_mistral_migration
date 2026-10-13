from functools import wraps
import os

def with_static_path(func):
    @wraps(func)
    def wrapper(story: str, filename: str = "story.mp3"):
        static_audio_path = os.path.join("static", "audio", filename)
        os.makedirs(os.path.dirname(static_audio_path), exist_ok=True)
        return func(story, static_audio_path)
    return wrapper

@with_static_path
def openai_text_to_speech(story, static_audio_path):
    pass
    # init + call API + save to static_audio_path
