# from fastapi import APIRouter
# from pydantic import BaseModel

# from mistralai import Mistral
from mistralai.client import Mistral
from src.config.settings import env_settings

mistral_client = Mistral(api_key=env_settings.mistral_api_key)

# def createSubjectsInfoDicts(squareCount, subjectsData): 
#     const subjects = []
#     for (let i = 0; i < squareCount; i++) {
#       subjects.push({
#         id: f"square-${i + 1}",
#         topic: subjectsData[i].topic,
#         subcolor: subjectsData[i].subcolor,
#         name: subjectsData[i].name
#       });
#     }
#     return subjects;

def generate_subjects_with_mistralai(topic: str) -> dict:
    print("Generating subjects for topic: ", topic)
    try:
        # Define a simple prompt template for subject generation
        prompt_template = f'''Generate a list of 25 engaging and diverse subjects related to the topic: {topic}.
                          Each subject should be concise and relevant compared to each other for conceptual learning.
                          If the {topic}'s length is >100 char, compact it cleverly before generating the subjects.
                          ## OUTPUT FORMAT:
                          a JSON dictionary with two keys: -'full_subjects:' -'compact_subjects:' containing each a list of 25 subjects as strings,
                          each list represents the subjects in their full and compact versions respectively.
                          ** ex format **:
                          {{
                            'full_subjects': ['subject 1', 'subject 2', ..., 'subject 25'],
                            'compact_subjects': ['compact subject 1', 'compact subject 2', ..., 'compact subject 25']
                          }}'''

        response = mistral_client.chat.complete(
            model="mistral-medium-latest",
            messages=[
                {
                    "content": prompt_template,
                    "role": "system"
                },
                {
                    "content": "Please provide the subjects by following the system instructions.",
                    "role": "user"
                },
                
            ],
            max_tokens=300,
            temperature=0.7,
            presence_penalty=0.5,
            stream=False)
        
        print(f"Response type: {type(response)}")

        if not response or not response.choices:
            raise ValueError("Empty response from Mistral API")

        full_subjects = response.choices[0].message.content[0] if response else "" # get the generated full subjects text
        compact_subjects = response.choices[0].message.content[1] if response else "" # get the generated compact subjects text
        print(f"Generated compact subjects text: {compact_subjects}")
        
        return full_subjects, compact_subjects

        # Parse the subjects from the response text
    #     subjects = []
    #     for line in subjects_text.split('\n'):
    #         line = line.strip()
    #         if line and any(char.isalnum() for char in line):
    #             # Remove numbering if present
    #             subject = line.split('.', 1)[-1].strip() if '.' in line else line
    #             subjects.append(subject)

    #     # Ensure we have exactly 25 subjects
    #     subjects = subjects[:25 if len(subjects) >= 25 else subjects + ["Subject Placeholder"] * (25 - len(subjects))
    
    #     return {"subjects": subjects}
    
    except Exception as e:
        print(f"Error generating subjects: {e}")
        return {"subjects": ["Subject Placeholder"] * 25}
