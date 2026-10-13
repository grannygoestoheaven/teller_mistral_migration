from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class TopicRequest(BaseModel):
    topic: str

class TopicCheckResponse(BaseModel):
    topic_filename: str = Field(alias="topicFilename")
    topic: str = Field(alias="topic")
    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True
    )
       