import os
import tempfile
import random
import base64
# import pyttsx3  # Local TTS library for testing purposes

from src.schemas.tts import TtsRequest # Pydantic model for TTS request
from src.config.settings import env_settings # Environment settings like API keys
from src.services.utils import _format_mp3_filename # Helper function to format filenames

from openai import OpenAI  # OpenAI API client
from elevenlabs.client import ElevenLabs # ElevenLabs API client
from mistralai.client import Mistral # Mistral API client
# from mistralai import Mistral # Mistral API client

openai_client = OpenAI(api_key=env_settings.openai_api_key)
elevenlabs_client = ElevenLabs(api_key=env_settings.elevenlabs_api_key)
mistral_client = Mistral(api_key=env_settings.mistral_api_key)

def openai_tts(story: TtsRequest, filename) -> bytes:
# def openai_tts(story: TtsRequest) -> bytes:
    """
    Generates speech from text using OpenAI's TTS and saves it to a static directory.

    Args:
        story: The text content of the story.
        filename: The desired filename for the audio (e.g., 'my_story.mp3').
        pause_between_sentences_ms: Duration of pause between sentences in milliseconds (default: 500ms).

    Returns:
        The path to the saved audio file
        (e.g., 'audio/generated_stories/my_story.mp3'), or None on error.
    """
    print(f"Entering openai_tts with story: {story}")
    # print(f"Entering openai_tts with story: {story} and filename: {filename}")
    try:
        # Ensure the input text is not empty and is a string
        if not story or not isinstance(story, str):
            raise ValueError("Story text must be a non-empty string")
        
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=story.strip(),  # Ensure we're passing a clean string
            response_format="mp3",
        #     instructions='''
        #                 Tone : discreet, tired.
        #                 Pacing : slow.
        #                 Emotional Range : peaceful.
        #                 ''',
        )
        
        speech_filename = _format_mp3_filename(filename) # generate an mp3 filename with underscores
        speech_audio = response.content
        
        print(f"Generated speech length: {len(speech_audio)} bytes")  # Should match expected size
        
        return speech_filename, speech_audio
        # return speech_audio

    except Exception as e:
        # Log the error appropriately in a real application
        print(f"Error in openai_tts: {e}")
        return None
    
def local_pyttsx3_tts(story: str, filename: str = "story.wav") -> str:
    """
    Generates speech from text using pyttsx3 and saves it to a static directory.

    Args:
        story: The text content of the story.
        filename: The desired filename for the audio (e.g., 'my_story.wav').

    Returns:
        The path to the saved audio file relative to the 'static' directory,
        or None if an error occurs.
    """
    try:
        # Initialize pyttsx3 engine
        engine = pyttsx3.init()
        
        # Create output directory if it doesn't exist
        if not filename.lower().endswith('.wav'):
            filename = f"{os.path.splitext(filename)[0]}.wav"
            
        output_path = os.path.join('static', GENERATED_STORIES_SUBDIR, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate and save speech
        engine.save_to_file(story, output_path)
        engine.runAndWait()
        
        # Return path relative to static directory
        return os.path.join(GENERATED_STORIES_SUBDIR, filename)
        
    except Exception as e:
        print(f"Error in local pyttsx3 TTS: {str(e)}")
        return None

def elevenlabs_text_to_speech(story: TtsRequest, filename) -> bytes:

    # Define the text and parameters
    text = story
    # voice_id = "JBFqnCBsd6RMkjVDRZzb"
    voice_id = "TSJI8fwfHJTx0WdruWnc" # American monotone 2 - custom voice made on eleven website
    model_id = "eleven_v3"
    output_format = "mp3_22050_32"

    # Generate speech
    audio = elevenlabs_client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format
    )
    
    audio_bytes = b"".join(chunk for chunk in audio)
    speech_filename = _format_mp3_filename(filename) # generate an mp3 filename with underscores
    
    return speech_filename, audio_bytes

    # we could return the audio bytes here, but we'll save it to a file instead

    # Save the audio
    # with open(speech_filename, "wb") as file:
    #     file.write(audio)
    
    # Return the audio bytes    
    # with open(speech_filename, "rb") as file:
    #     audio_bytes = file.read()
    
def mistral_tts(story: TtsRequest, filename) -> bytes:
    """
    """
    try:
    # Ensure the input text is not empty and is a string
        if not story or not isinstance(story, str):
            raise ValueError("Story text must be a non-empty string")
        
        response = mistral_client.audio.speech.complete(
            model="voxtral-mini-tts-2603",
            input=story.strip(),
            # voice_id='e3596645-b1af-469e-b857-f18ddedc7652', # 'oliver' neutral
            voice_id='530e2e20-58e2-45d8-b0a5-4594f4915944', # 'paul' sad
            response_format="mp3",
        )
        
        speech_filename = _format_mp3_filename(filename) # generate an mp3 filename with underscores
        speech_audio = base64.b64decode(response.audio_data)
        print(speech_audio[:20])  # Print the first few bytes to verify it's audio data
        
        print(f"Generated speech length: {len(speech_audio)} bytes")  # Should match expected size
        
        return speech_filename, speech_audio

    except Exception as e:
        # Log the error appropriately in a real application
        print(f"Error in openai_tts: {e}")
        return None
    return None
