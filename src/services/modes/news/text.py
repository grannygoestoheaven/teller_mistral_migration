@router.post('/news') 
def generate_news_with_mistral_chat(news_text: str, pattern: str, estimated_chars: int) -> tuple[str, str]:
    """
    Generates a factual, styled presentation using Mistral-Large,
    enabling premium web search for up-to-date and verified information.

    Args:
        subject: The core topic of the presentation (e.g., "AI ethics in 2025").
        pattern: The core system prompt/pattern for the model's behavior.
        
    Returns:
        tuple: (story_text, output_filename)
    """
    
    # 1. ENHANCE SYSTEM MESSAGE (INSTRUCTION TO USE TOOL)
    # The system message explicitly tells the model it has a tool and must use it.
    system_message = f"""{pattern}
    You are an expert on writing concise, clear, and factual news presentation on the {news_text} provided.
    
    Ensure all claims are grounded in the search results.
    - Focus specifically on: {subject}
    - Keep it around {estimated_chars} characters long.
    - Be factual, clear and precise. No generalities.
    - Make the text four paragraphs long.
    - Initiate the text with a soft, quiet opening (e.g., a raw list of a few slightly unexpected concepts that will be covered). **Always pick concepts slighlty more unexpected than normal.**
    - Always add a new line after the opening.
    - Add <[silence]> tags between all sentences and between each new line.
    - Conclude by suggesting three related subjects to the topic, in variations of this kind : "Three related subjects are...". Don't write anything after that.
    
    ## Unavoidable Instructions:
    - Write in an elegant style, not in a grandiose style. Avoid any mystery tone at all cost.
    - Do not use cliches or jargon.
    - Use absolutely ZERO cliches or jargon or journalistic language like "In a world, in the realm", etc.
    - Forbidden extreme words = "crucial", "essential", "critical", "fundamental" etc.
    - USE ZERO poetry of any kind.
    - Use ZERO metaphor of any kind.
    - use ZERO common setup language in any sentence, including: in conclusion, in closing, etc.
    - Do not output warnings or notes—just the output requested."""
    
    # 2. CONSTRUCT USER MESSAGE
    user_message =f"""Please generate faithful presentation about: {subject}"""

    try:
        # 3. MISTRAL AGENT API CALL
        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=[
                {
                    "content": system_message,
                    "role": "system"
                },
                {
                    "content": user_message,
                    "role": "user"
                }
            ],
            frequency_penalty=0.1,
            temperature=0.4,
            max_tokens=1150,
        )

        if not response.choices:
            return "Mistral API did not return any outpus.", "error.mp3"
            
        content = response.choices[0].message.content.strip()
        if not content:
            return "Received empty response from Mistral API.", "error.mp3"
        
        # Use the original subject for the filename, not the AI-generated title
        filename = _format_mp3_filename(subject)
        
        return content, filename
        
    except Exception as e:
        error_msg = f"Error calling Mistral API: {str(e)}"
        print(error_msg)
        return "We encountered an error while generating the story. Please try again.", "error.mp3"
    
def generate_news_with_mistral_agent(subject: str) -> tuple[str, str]:
    with Mistral(
        api_key=os.getenv("MISTRAL_API_KEY"),
    ) as mistral:

        res = mistral.agents.complete(messages=[
            {
                "SystemMessage": system_message,
                "content": subject,
                "role": "user",
            },
        ], agent_id="<id>", stream=False)

        # Handle response
        return 
