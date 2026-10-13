from elevenlabs.client import ElevenLabs

from src.config.settings import env_settings

elevenlabs_client = ElevenLabs(api_key=env_settings.elevenlabs_api_key)

def elevenlabs_soundscape(prompt):
    model_id = "eleven_text_to_sound_v2"
    output_format = "mp3_22050_32"
    
    audio = elevenlabs_client.text_to_sound_effects.convert(
        prompt=str, 
        loop=True, 
        duration=20
    )

    return audio
