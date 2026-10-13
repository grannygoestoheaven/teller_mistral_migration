class NewsResponse(BaseModel):
    title: str
    source: str
    summary: str  # Max 3 sentences
