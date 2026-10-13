from fastapi import APIRouter
from src.schemas.news import NewsItem

router = APIRouter()

# @router.get("/news/check_report")
# async def teller_new

# @router.get("/news/new_report", response_model=NewsResponse)
# async def new_report(data: NewsRequest -> NewsResponse):
#     try:
#         subject = data.subject
#         narrative_style = data.narrative_style
#         difficulty = data.difficulty
        
#         payload = build_story(subject, narrative_style, difficulty)
        
#         return NewsResponse(**payload, by_alias=True)
    
#     except Exception as e:
#     print(f"ERROR: {str(e)}")  # Log the error
#     raise HTTPException(status_code=500, detail=str(e))
