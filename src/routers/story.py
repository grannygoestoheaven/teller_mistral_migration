import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.schemas.story import StoryRequest, StoryResponse, StoryCheckResponse
from src.services.utils import _format_text_filename, _clean_story_title
from src.services.build import build_story, load_story
from src.config.settings import env_settings, BASE_DIR, DATA_DIR, DEFAULT_PROMPT_PATH, PROMPTS
from src.services.storage import StorageBackend

router = APIRouter()
storage = StorageBackend(use_bucket=env_settings.use_bucket, settings=env_settings)

#loading endpoint for an existing story
@router.post("/check_story", response_model=StoryCheckResponse)
def check_story(data: StoryRequest) -> StoryCheckResponse:
    print("entering check_story endpoint")
    try:
        subject = data.subject
        print(f"Received subject: {subject}")  # Debug print to verify subject
        # pace = data.pace
        # print(pace)
        filename = _format_text_filename(subject)
        foldername = _format_text_filename(subject)
        # foldername = _format_text_filename(subject, pace)
        # filename = _format_text_filename(subject, pace)
        print(foldername, filename)

        if storage.use_bucket:
            try:
                # key = f"stories/{filename}/{filename}.json" # we'll have to update the path for the bucket to have a parent folder {narrative_style}
                key = f"stories/{foldername}/{filename}.json" # we'll have to update the path for the bucket to have a parent folder {narrative_style}
                storage.client.download_file(key)
                story_exists = True
            except Exception as e:
                print(f"Story not found in bucket: {str(e)}")
                story_exists = False
        else:
            # json_path = DATA_DIR / "stories" / filename / f"{filename}.json" 
            json_path = DATA_DIR / "stories" / foldername / f"{filename}.json"
            print(f"Checking for story at path: {json_path}")
            story_exists = json_path.exists()
            # mp3_path = DATA_DIR / "stories" / filename / f"{filename}.mp3"

        if not story_exists:
            return {"exists": False, "story": None}

        payload = load_story(subject, regenerate_mp3=True) # The load story function holds the condition to generate tts if missing.
        return {"exists": True, "story": StoryResponse(**payload, by_alias=True)}
    
    except Exception as e:
        print(f"ERROR: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=str(e))
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)})

# generation endpoint for an unexisting story
@router.post("/new_story", response_model = StoryResponse)
def new_story(data: StoryRequest) -> StoryResponse:
    try:
        subject = data.subject # str
        temperature = data.temperature or 0.3 # float
        # pace = data.pace # bool
        length = data.length or 1500 # int defining the max_tokens for the story generation. We can adjust it according to the desired story length and the model's token limits.
        narrative_style = data.narrative_style or DEFAULT_PROMPT_PATH
        difficulty = data.difficulty or "beginner"
        # difficulty = data.difficulty or "intermediate"
        # difficulty = data.difficulty or "expert"
        
        # print(f"pace value : {pace}")
        print(f"Hello Server {data.subject}")  # Debug print to verify subject

        # payload = build_story(subject, pace, narrative_style, difficulty) # the build story function generates both text then sends it to tts.
        payload = build_story(subject, temperature, length, narrative_style, difficulty) # the build story function generates both text then sends it to tts.
        # print(f"Payload from build_story: {payload}")  # Debug print to verify payload
        return StoryResponse(**payload, by_alias=True)
    
    except Exception as e:
        print(f"ERROR: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/share/{subject}", response_model=dict)
async def generate_share_link(subject: str) -> dict:
    try:
        # Clean the subject to match the filename format
        filename = _format_text_filename(subject)

        # Check if story exists (reuse logic from check_story)
        if storage.use_bucket:
            try:
                key = f"stories/{filename}/{filename}.json"
                storage.client.download_file(key)
                story_exists = True
            except Exception as e:
                print(f"Story not found in bucket: {str(e)}")
                story_exists = False
        else:
            json_path = DATA_DIR / "stories" / filename / f"{filename}.json"
            story_exists = json_path.exists()

        if not story_exists:
            return {"error": "Story not found", "share_url": None}

        # Generate shareable URL
        share_url = f"/shared_story/{filename}"

        return {
            "share_url": share_url,
            "subject": subject,
            "filename": filename
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
