from pydantic import BaseModel, Field

class TtsRequest(BaseModel):
    text: str

class TtsResponse(BaseModel):
    speech_filename: str = Field(alias="speechFilename")  # Raw speech filename
    speech_file: bytes = Field(alias="speechFile")        # Speech audio file in bytes
    
    class Config:
        populate_by_name = True
        validate_by_name = True
