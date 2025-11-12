"""FastAPI application exposing the mental health tiered care calculator."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import logic
from .models import (
    CSSRSRequest,
    CSSRSResponse,
    ErrorResponse,
    GAD7Response,
    PHQ4Response,
    PHQ9Response,
    QuestionnaireDefinition,
    QuestionnaireRequest,
    TierRequest,
    TierResponse,
)
from .questionnaires import get_questionnaire, list_questionnaires

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "index.html"

app = FastAPI(
    title="Mental Health Tiered Care API",
    description="Logic engine for administering PHQ-4, PHQ-9, GAD-7, and C-SSRS questionnaires.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    """Serve the single page application."""

    if not INDEX_FILE.exists():
        raise HTTPException(status_code=404, detail="User interface has not been built.")
    return FileResponse(INDEX_FILE)


@app.get("/api/questionnaires", response_model=list[QuestionnaireDefinition])
def get_questionnaires() -> list[Dict[str, object]]:
    """Return metadata for all questionnaires."""

    return list_questionnaires()


@app.get(
    "/api/questionnaires/{name}",
    response_model=QuestionnaireDefinition,
    responses={404: {"model": ErrorResponse}},
)
def get_questionnaire_endpoint(name: str) -> Dict[str, object]:
    """Return a specific questionnaire definition."""

    try:
        questionnaire = get_questionnaire(name)
    except KeyError as exc:  # pragma: no cover - FastAPI handles
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return questionnaire


@app.post(
    "/api/assessments/phq4",
    response_model=PHQ4Response,
    responses={400: {"model": ErrorResponse}},
)
def assess_phq4(request: QuestionnaireRequest) -> Dict[str, object]:
    """Score the PHQ-4 and determine next steps."""

    try:
        subscores = logic.score_phq4(request.responses)
        followup = logic.followup_from_phq4(subscores)
    except logic.QuestionnaireScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        **subscores,
        **followup,
    }


@app.post(
    "/api/assessments/phq9",
    response_model=PHQ9Response,
    responses={400: {"model": ErrorResponse}},
)
def assess_phq9(request: QuestionnaireRequest) -> Dict[str, object]:
    """Score the PHQ-9 questionnaire."""

    try:
        result = logic.score_phq9(request.responses)
    except logic.QuestionnaireScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


@app.post(
    "/api/assessments/gad7",
    response_model=GAD7Response,
    responses={400: {"model": ErrorResponse}},
)
def assess_gad7(request: QuestionnaireRequest) -> Dict[str, object]:
    """Score the GAD-7 questionnaire."""

    try:
        result = logic.score_gad7(request.responses)
    except logic.QuestionnaireScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


@app.post(
    "/api/assessments/cssrs",
    response_model=CSSRSResponse,
    responses={400: {"model": ErrorResponse}},
)
def assess_cssrs(request: CSSRSRequest) -> Dict[str, object]:
    """Evaluate risk level based on the C-SSRS screener."""

    try:
        result = logic.evaluate_cssrs(request.responses)
    except logic.QuestionnaireScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


@app.post(
    "/api/assessments/tier",
    response_model=TierResponse,
    responses={400: {"model": ErrorResponse}},
)
def determine_tier_endpoint(request: TierRequest) -> Dict[str, object]:
    """Combine PHQ-9 and GAD-7 scores to produce a service tier recommendation."""

    try:
        result = logic.determine_tier(request.phq9_total, request.gad7_total)
    except logic.QuestionnaireScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result

