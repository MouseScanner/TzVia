from pydantic import BaseModel
from typing import List, Optional, Any

class ReviewCreate(BaseModel):
    text: str
    sentiment: int

class ReviewResponse(BaseModel):
    id: int
    text: str
    sentiment: int

class SimilarityRequest(BaseModel):
    text: str

class SimilarReview(BaseModel):
    text: str
    sentiment: int
    distance: float

class SimilarityResponse(BaseModel):
    similar_reviews: List[SimilarReview]

class TaskResponse(BaseModel):
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None 