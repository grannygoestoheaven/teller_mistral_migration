import os
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.schemas.story import StoryRequest, StoryResponse, StoryCheckResponse
from src.services.utils import _format_text_filename, _find_story_id_by_filename
from src.services.build import build_story, load_story
from src.config.settings import env_settings, BASE_DIR, DATA_DIR, DEFAULT_PROMPT_PATH, PROMPTS
from src.services.storage import StorageBackend

router = APIRouter()
storage = StorageBackend(use_bucket=env_settings.use_bucket, settings=env_settings)
manifest_path = DATA_DIR / "stories/manifest.json"

#loading endpoint for an existing story
@router.post("/check_story", response_model=StoryCheckResponse)
async def check_story(data: StoryRequest) -> StoryCheckResponse:
    try:
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                
        subject = data.subject
        filename = _format_text_filename(subject)
        story_id = _find_story_id_by_filename(filename, manifest) # Implement this function to search for the story ID based on the filename in your storage system

        if storage.use_bucket:
            try:
                key = f"stories/{story_id}/{story_id}.json" # we'll have to update the path for the bucket to have a parent folder {narrative_style}
                storage.client.download_file(key)
                story_exists = True
            except Exception as e:
                print(f"Story not found in bucket: {str(e)}")
                story_exists = False
        else:
            json_path = DATA_DIR / "stories" / story_id / f"{story_id}.json"
            story_exists = json_path.exists()
            # mp3_path = DATA_DIR / "stories" / story_id / f"{story_id}.mp3"

        if not story_exists:
            return {"exists": False, "story": None}

        payload = load_story(story_id, subject, regenerate_mp3=True) # The load story function holds the condition to generate tts if missing.
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
        subject = data.subject
        print(f"Hello Server {data.subject}")  # Debug print to verify subject
        narrative_style = data.narrative_style or DEFAULT_PROMPT_PATH
        difficulty = data.difficulty or "beginner"
        # difficulty = data.difficulty or "intermediate"
        # difficulty = data.difficulty or "expert"

        payload = build_story(subject, narrative_style, difficulty) # the build story function generates both text then sends it to tts.
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
