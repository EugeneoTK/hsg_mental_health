"""Pydantic models for request and response payloads."""
from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field, validator


class QuestionnaireRequest(BaseModel):
    responses: Dict[str, int] = Field(..., description="Mapping of question id to selected score")

    @validator("responses")
    def ensure_non_empty(cls, value: Dict[str, int]) -> Dict[str, int]:
        if not value:
            raise ValueError("At least one response must be provided.")
        return value


class PHQ4Response(BaseModel):
    total_score: int
    depression_score: int
    anxiety_score: int
    recommend_phq9: bool
    recommend_gad7: bool
    message: str


class PHQ9Response(BaseModel):
    total_score: int
    item_9_score: int
    severity: str
    recommend_cssrs: bool
    message: str


class GAD7Response(BaseModel):
    total_score: int
    severity: str


class CSSRSRequest(BaseModel):
    responses: Dict[str, int]


class CSSRSResponse(BaseModel):
    risk_level: str
    description: str


class TierRequest(BaseModel):
    phq9_total: Optional[int] = Field(None, ge=0, le=27)
    gad7_total: Optional[int] = Field(None, ge=0, le=21)

    @validator("phq9_total", "gad7_total", pre=True)
    def allow_empty_string(cls, value: Optional[int]) -> Optional[int]:
        if value == "" or value is None:
            return None
        return value


class TierResponse(BaseModel):
    tier: Dict[str, object]
    tool_breakdown: Dict[str, Dict[str, int]]


class QuestionnaireDefinition(BaseModel):
    id: str
    title: str
    description: str
    questions: list


class ErrorResponse(BaseModel):
    detail: str

