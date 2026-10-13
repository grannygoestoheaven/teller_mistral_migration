import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.routers import topic, story, media
from src.config.settings import env_settings, load_prompts

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(topic.router, prefix="/v1/topic")
# app.include_router(story.router, prefix="/v1/stories")
# app.include_router(media.router, prefix="")

app.include_router(topic.router, prefix="/api/v1/topic")
app.include_router(story.router, prefix="/api/v1/stories")
app.include_router(media.router, prefix="/api")

app.mount("/", StaticFiles(directory="dist", html=True)) # serves the built React frontend (npm run build)
# app.mount("/", StaticFiles(directory="/app/teller_vite/dist", html=True)) # for docker. the container is running in /app

print(app.routes)

@app.on_event("startup")
def startup_event():
    load_prompts()  # Load all prompts once at startup

print("Server running at: http://127.0.0.1:8000")

# @app.get("/static/{file_path:path}")
# async def serve_static(file_path: str):
#     return FileResponse(
#         Path("static") / file_path,
#         headers={"Access-Control-Allow-Origin": "*"}
#     )

# app.include_router(ui_home.router)
