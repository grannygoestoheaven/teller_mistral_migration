from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from src.config.settings import DATA_DIR

router = APIRouter()

@router.get("/tracks/{file_path:path}")
async def serve_tracks(file_path: str):
    return FileResponse(
        DATA_DIR / "audio" / "local_ambient_tracks" / file_path,
        media_type="audio/mpeg",
        headers={"Access-Control-Allow-Origin": "*"}
    )

@router.get("/speeches/{story_name}/{file_path:path}")
async def serve_story_audio(story_name: str, file_path: str):
    file_location = DATA_DIR / "stories" / story_name / file_path
    print(f"Looking for file at: {file_location}")  # Debug line
    return FileResponse(
        file_location,
        media_type="audio/mpeg",
        headers={"Access-Control-Allow-Origin": "*"}
    )
