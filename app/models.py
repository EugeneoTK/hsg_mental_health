"""Pydantic models for request and response payloads."""
from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field, root_validator, validator


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


class MentalHealthSummaryRequest(BaseModel):
    """Payload produced by the front-end summary form."""

    phq4_depression: int = Field(..., ge=0, le=6)
    phq4_anxiety: int = Field(..., ge=0, le=6)
    phq9_total: Optional[int] = Field(None, ge=0, le=27)
    gad7_total: Optional[int] = Field(None, ge=0, le=21)
    rating: Optional[int] = Field(None, ge=1, le=5)
    responses: Dict[str, int] = Field(default_factory=dict)

    @validator("phq4_depression", "phq4_anxiety", pre=True)
    def _coerce_required_int(cls, value: object) -> int:
        try:
            return int(value)  # type: ignore[return-value]
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError("PHQ-4 subscores must be integers") from exc

    @validator("phq9_total", "gad7_total", "rating", pre=True)
    def _coerce_optional_int(cls, value: object) -> Optional[int]:
        if value in (None, ""):
            return None
        try:
            return int(value)  # type: ignore[return-value]
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise ValueError("Field must be an integer if provided") from exc

    @root_validator(pre=True)
    def _collect_responses(cls, values: Dict[str, object]) -> Dict[str, object]:
        responses: Dict[str, int] = {}
        for key, raw in list(values.items()):
            if not isinstance(key, str):
                continue
            if key.startswith("phq9_q") or key.startswith("gad7_q"):
                try:
                    responses[key] = int(raw)  # type: ignore[arg-type]
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Response for {key} must be an integer") from exc
        values.setdefault("responses", responses)
        return values


class MentalHealthSummaryResponse(BaseModel):
    """Structured summary returned to the HTML client."""

    screening_summary: str
    recommended_actions: str
    service_tier: str
    feedback: Optional[str] = None

