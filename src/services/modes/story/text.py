import os
import math  # For character-to-token conversion
import re

from mistralai.client import Mistral
# from mistralai import Mistral
from openai import OpenAI

from jinja2 import Template

from src.config.settings import env_settings
from src.config.pacing_engine_functions import _apply_silence_tags, silence_map_variations_short_openai_tts, silence_map_elevenlabs_tts, silence_map_variations_voxtral_tts
from src.services.utils import _clean_story_text, _remove_silence_tags, _format_text_filename, _clean_story_title

mistral_client = Mistral(api_key=env_settings.mistral_api_key)
openai_client = OpenAI(api_key=env_settings.openai_api_key)

def generate_story_with_mistralai(subject, temperature: None, length: None, narrative_style: None, difficulty: None) -> tuple[str, str]:
    print("entering Mistral story: ", subject, narrative_style, difficulty)
    try:
        # 1. Read the prompt template from the file
        with open(narrative_style, "r") as f:
            print("Opened narrative style file successfully.")
            narrative_style_template = Template(f.read())
            narrative_style_rendered = narrative_style_template.render(     
                subject = subject,
                difficulty = difficulty
            )

        print(f" Let's see : {narrative_style_rendered[:50]}")
        print(f"text subject: {subject}")
            
        response = mistral_client.chat.complete(
            model="mistral-medium-latest",
            messages=[
                {
                    "content": narrative_style_rendered,
                    "role": "system"
                },
                {
                    # "content": f"generate a 1050 char MAXIMUM text about {subject}.",
                    "content": f"generate a {length} char MAXIMUM text about {subject}.",
                    # "content": f"generate a 600 char MAXIMUM text about {subject}.",
                    "role": "user"
                },
                
            ],
            max_tokens=length,
            # temperature=0.2,
            temperature=temperature,
            presence_penalty=1.2,
            stream=False)
        
        print(f"Response type: {type(response)}")

        if not response or not response.choices:
            raise ValueError("Empty response from Mistral API")

        original_output = response.choices[0].message.content if response else ""
        original_output = original_output.replace("*", "").replace("**", "")
        print(f"GENERATED OUTPUT: {original_output}")

        silences = silence_map_variations_short_openai_tts # Define your silence mapping here or import it from config
        # silences = silence_map_elevenlabs_tts # Define your silence mapping here or import it from config
        # silences = silence_map_variations_voxtral_tts

        tts_text = _apply_silence_tags(original_output, silences)
        print(f"TTS TEXT WITH SILENCE TAGS: {tts_text}")
        clean_story_title = _clean_story_title(subject)
    
        return clean_story_title, tts_text, original_output
        # return clean_story_title, original_output, original_output # >> no silence tags - default tts behavior (mistral tts do not accept tags)
    
    except Exception as e:
        print(f"Full error: {e[:20]}")  # Log both error and response
        error_title = f"Error generating story about {subject}"
        error_story = "We encountered an error while generating the story. Please try again."
        
        return error_story, error_story, _format_text_filename(error_title) + ".mp3"

def generate_story_with_openai_jinja(subject, narrative_style: None, difficulty: None) -> tuple[str, str]:
    print("entering Mistral story: ", subject, narrative_style, difficulty)
    try:
        # 1. Read the prompt template from the file
        with open(narrative_style, "r") as f:
            narrative_style_template = Template(f.read())
            print(f"narrative_style_temp: {narrative_style_template}")  # Debug print to verify template content
            narrative_style_rendered = narrative_style_template.render(
                subject = subject,
                difficulty = difficulty
            )

        print(f" Let's see : {narrative_style_rendered}")

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": narrative_style_rendered},
                {"role": "user", "content": "follow the system instructions and generate a text of **MAX 1630 characters.**"}
            ],
            temperature=0.2,
            presence_penalty=0.3,
            max_tokens=1001
        )

        print(f"Response from OpenAI: {response}")
        tagged_story_for_tts = response.choices[0].message.content.strip() if response else "" # get the story text with punctuation tags
        print(f"Generated tagged story for TTS: {tagged_story_for_tts}")
        clean_story = _clean_story_text(tagged_story_for_tts) # remove punctuation tags to have a clean version to display
        clean_story_title = _clean_story_title(subject)
       
        return clean_story_title, tagged_story_for_tts, clean_story
    
    except Exception as e:
        print(f"Error in generating_story: {str(e)}")
        error_title = f"Error generating story about {subject}"
        error_story = "We encountered an error while generating the story. Please try again."
        
        return error_story, _format_text_filename(error_title) + ".mp3"
    