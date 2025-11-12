"""FastAPI application exposing the mental health tiered care calculator."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

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
    MentalHealthSummaryRequest,
    MentalHealthSummaryResponse,
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
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_CANDIDATES = [
    FRONTEND_DIR / "index.html",
    STATIC_DIR / "index.html",
]

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

    for candidate in INDEX_CANDIDATES:
        if candidate.exists():
            return FileResponse(candidate)

    raise HTTPException(status_code=404, detail="User interface has not been built.")


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


@app.post(
    "/api/mental-health",
    response_model=MentalHealthSummaryResponse,
    responses={400: {"model": ErrorResponse}},
)
def summarise_mental_health(request: MentalHealthSummaryRequest) -> MentalHealthSummaryResponse:
    """Aggregate questionnaire responses into narrative guidance for the front-end."""

    followup = logic.followup_from_phq4(
        {
            "depression_score": request.phq4_depression,
            "anxiety_score": request.phq4_anxiety,
        }
    )

    screening_bits = [
        f"<p><strong>PHQ-4 depression sub-score:</strong> {request.phq4_depression}</p>",
        f"<p><strong>PHQ-4 anxiety sub-score:</strong> {request.phq4_anxiety}</p>",
    ]
    recommended_bits = [f"<p>{followup['message']}</p>"]

    phq9_result: Optional[Dict[str, object]] = None
    if request.phq9_total is not None:
        phq9_responses = {k: v for k, v in request.responses.items() if k.startswith("phq9_q")}
        try:
            phq9_result = logic.score_phq9(phq9_responses)
        except logic.QuestionnaireScoringError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        screening_bits.append(
            f"<p><strong>PHQ-9 total:</strong> {phq9_result['total_score']} "
            f"({phq9_result['severity']} severity)</p>"
        )
        recommended_bits.append(f"<p>{phq9_result['message']}</p>")
        if phq9_result.get("item_9_score", 0) and int(phq9_result["item_9_score"]) > 0:
            recommended_bits.append(
                "<p><strong>Safety alert:</strong> Item 9 is positive. Ensure immediate safety assessment.</p>"
            )

    gad7_result: Optional[Dict[str, object]] = None
    if request.gad7_total is not None:
        gad7_responses = {k: v for k, v in request.responses.items() if k.startswith("gad7_q")}
        try:
            gad7_result = logic.score_gad7(gad7_responses)
        except logic.QuestionnaireScoringError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        screening_bits.append(
            f"<p><strong>GAD-7 total:</strong> {gad7_result['total_score']} "
            f"({gad7_result['severity']} severity)</p>"
        )

    tier_section = (
        "<p>Tier recommendation becomes available once PHQ-9 or GAD-7 totals are provided.</p>"
    )
    if phq9_result or gad7_result:
        try:
            tier_info = logic.determine_tier(
                int(phq9_result["total_score"]) if phq9_result else request.phq9_total,
                int(gad7_result["total_score"]) if gad7_result else request.gad7_total,
            )
        except logic.QuestionnaireScoringError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        tier = tier_info["tier"]
        breakdown_segments = []
        for tool, data in tier_info["tool_breakdown"].items():
            breakdown_segments.append(
                f"<p><em>{tool.upper()} score:</em> {data['score']} "
                f"(Tier {data['tier']})</p>"
            )
        tier_section = (
            f"<p><strong>{tier['name']}:</strong> {tier['label']}</p>"
            f"<p>{tier['description']}</p>"
            + "".join(breakdown_segments)
        )

    feedback_section: Optional[str] = None
    if request.rating is not None:
        feedback_section = (
            "<p>Thanks for rating the experience. Feedback is logged anonymously to improve the toolkit.</p>"
        )

    return MentalHealthSummaryResponse(
        screening_summary="".join(screening_bits),
        recommended_actions="".join(recommended_bits),
        service_tier=tier_section,
        feedback=feedback_section,
    )

