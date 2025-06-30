from pydantic import BaseModel, Field
from typing import Optional


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to analyze for sentiment")


class SentimentResponse(BaseModel):
    label: str = Field(..., description="Sentiment label (POSITIVE or NEGATIVE)")
    score: float = Field(..., description="Confidence score between 0 and 1")
    text: str = Field(..., description="Original input text")
    request_id: Optional[str] = Field(None, description="Unique request identifier")