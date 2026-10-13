from pydantic import BaseModel, Field
from typing import Optional

# text and audio schemas request
class StoryRequest(BaseModel):
    subject: str
    # pace: Optional[bool] = False
    temperature: Optional[float] = 0.2
    length: Optional[int] = None
    narrative_style: str | None = None
    difficulty: str | None = None

# text and audio schemas response
class StoryResponse(BaseModel):
    story_filename: str = Field(alias="storyFilename")  # raw filename
    story_title: str = Field(alias="storyTitle")        # cleaned title   
    story: str = Field(alias="story")                   # cleaned story text
    speech_url: str = Field(alias="speechUrl")        # url to speech
    track_url: str = Field(alias="trackUrl")            # url to track
    track_title: str = Field(alias="trackTitle")        # clean track filename
    
    class Config:
        populate_by_name = True
        validate_by_name = True

class StoryCheckResponse(BaseModel):
    exists: bool
    story: Optional[StoryResponse] = None

class NewsItem(BaseModel):
    title: str
    source: str
    summary: str  # Max 3 sentences
