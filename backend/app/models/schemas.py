from typing import List, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Incoming request payload for the /agent endpoint
# ---------------------------------------------------------


class ResearchRequest(BaseModel):
    question: str
    thread_id: str


# ---------------------------------------------------------
# Reference object returned by the agent
# ---------------------------------------------------------


class Reference(BaseModel):
    doc_name: Optional[str] = None
    pages: Optional[List[int]] = None


# ---------------------------------------------------------
# API response object returned by /agent
# ---------------------------------------------------------


class ResearchResponse(BaseModel):
    answer: str = ""
    references: List[Reference] = Field(default_factory=list)
