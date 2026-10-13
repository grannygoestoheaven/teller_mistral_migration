from src.config.settings import env_settings
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

eleven_labs_client = ElevenLabs(api_key=env_settings.elevenlabs_api_key)

audio_speech = elevenlabs_client.text_to_speech.convert(
    text="The first move is what sets everything in motion.",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)

audio_effects = elevenlabs.text_to_sound_effects.convert(text="Cinematic Braam, Horror")

play(audio)
