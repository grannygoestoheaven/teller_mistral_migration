import re

def _apply_silence_tags(text: str, silence_map: dict) -> str:
    print("entering silence function")
    # Matches punct ONLY if followed by space or end of string
    pattern = r'(?<!\b[A-Z])(\.{3}|[.;?!—\n])(?=\s|$)'

    print(f"Using pattern: {pattern}")  
    
    def replace(m):
        p = m.group(1)
        return f"{p}<[silence:{silence_map[p]}ms]>"
        # return f"{p}{silence_map[p]}" # test for voxtral
    
    return re.sub(pattern, replace, text)

silence_map_super_short_openai_tts = {
    '.': 20,    # Standard pause
}

silence_map_openai_tts = {
    '\n': 1000,  # Newline pause
    '.': 400,    # Standard pause
    ';': 100,    # Short pause
    '...': 900,  # Dramatic pause
    ':': 100,    # Introduction pause
    '!': 400,    # Exclamatory pause
    '?': 100,    # Question pause
    '-': 100,    # Dash pause
    ',': 100,    # comma pause
    '(': 50,     # open parenthese pause
    ')': 50,     # close parenthese pause
}

silence_map_variations_openai_tts = {
    '.': 60,    # Standard pause
    ';': 80,    # Short pause
    '!': 110,    # Exclamatory pause
    '?': 110,    # Question pause
    '—': 70,    # Em dash pause
    ':': 80,    
}

silence_map_variations_short_openai_tts = {
    '.': 30,    # Standard pause
    ';': 20,    # Short pause
    '!': 30,    # Exclamatory pause
    '?': 30,    # Question pause
    '—': 20,    # Em dash pause
    '\n': 30,
}

silence_map_variations_long_openai_tts = {
    '.': 90,    # Standard pause
    ';': 100,    # Short pause
    '!': 130,    # Exclamatory pause
    '?': 130,    # Question pause
    '—': 90,    # Em dash pause
    ':': 100,    
}

silence_map_long_plus_openai_tts = {
    '.': 1300,    # Standard pause
    ';': 150,    # Short pause
    '!': 150,    # Exclamatory pause
    '?': 150,    # Question pause
    '—': 150,    # Em dash pause
    ':': 150,    
}

silence_map_long_openai_tts = {
    '.': 800,    # Standard pause
    ';': 100,    # Short pause
    '!': 100,    # Exclamatory pause
    '?': 100,    # Question pause
    '—': 100,    # Em dash pause
    ':': 100,
}

silence_map_medium_openai_tts = {
    '.': 500,    # Standard pause
    ';': 70,    # Short pause
    '!': 70,    # Exclamatory pause
    '?': 70,    # Question pause
    '—': 70,    # Em dash pause
    ':': 70,
}

silence_map_short_openai_tts = {
    '.': 30,    # Standard pause
    ';': 20,    # Short pause
    '!': 50,    # Exclamatory pause
    '?': 20,    # Question pause
    ':': 20,    # Introduction pause
    '—': 20,    # Em dash pause
}

silence_map_elevenlabs_tts = {
    '\n': "[long pause]",  # Newline pause
    '.': "[long pause]",    # Standard pause
    ';': "[pause]",    # Short pause
    ':': "[pause]",    # Introduction pause
    '!': "[long pause]",    # Exclamatory pause
    '?': "[long pause]",    # Question pause
    '-': "[pause]",    # Dash pause
    ',': "[pause]",    # comma pause
}

# a simple test for voxtral 
silence_map_variations_voxtral_tts = {
    '.': '...',    # Standard pause
    ';': '...',    # Short pause
    '!': '...',    # Exclamatory pause
    '?': '...',    # Question pause
    '—': '...',    # Em dash pause
    '\n': '...',
}
