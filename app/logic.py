"""Core scoring logic for the mental health assessments."""
from __future__ import annotations

from typing import Dict, Optional


class QuestionnaireScoringError(ValueError):
    """Raised when questionnaire responses are missing or invalid."""


def _validate_responses(responses: Dict[str, int], expected_ids: Optional[Dict[str, range]] = None) -> None:
    """Ensure all responses are present and within the valid range."""

    if not responses:
        raise QuestionnaireScoringError("No responses were provided.")

    for question_id, value in responses.items():
        if not isinstance(value, int):
            raise QuestionnaireScoringError(f"Response for {question_id} must be an integer.")
        if expected_ids and question_id in expected_ids:
            valid_range = expected_ids[question_id]
            if value not in valid_range:
                raise QuestionnaireScoringError(
                    f"Response for {question_id} must be within {valid_range.start}-{valid_range.stop - 1}."
                )

    if expected_ids:
        missing = set(expected_ids.keys()) - set(responses.keys())
        if missing:
            missing_ids = ", ".join(sorted(missing))
            raise QuestionnaireScoringError(f"Missing responses for: {missing_ids}.")


def score_phq4(responses: Dict[str, int]) -> Dict[str, int]:
    """Calculate PHQ-4 subscores and total."""

    expected_ids = {f"phq4_q{idx}": range(0, 4) for idx in range(1, 5)}
    _validate_responses(responses, expected_ids)

    depression_ids = ["phq4_q1", "phq4_q2"]
    anxiety_ids = ["phq4_q3", "phq4_q4"]

    depression_score = sum(responses[qid] for qid in depression_ids)
    anxiety_score = sum(responses[qid] for qid in anxiety_ids)
    total_score = depression_score + anxiety_score

    return {
        "total_score": total_score,
        "depression_score": depression_score,
        "anxiety_score": anxiety_score,
    }


def followup_from_phq4(subscores: Dict[str, int]) -> Dict[str, object]:
    """Determine which questionnaires should follow the PHQ-4 results."""

    depression_score = subscores["depression_score"]
    anxiety_score = subscores["anxiety_score"]

    recommend_phq9 = depression_score >= 3
    recommend_gad7 = anxiety_score >= 3

    if not recommend_phq9 and not recommend_gad7:
        message = (
            "Monitor symptoms and consider psychoeducation. No additional screening is required at this time."
        )
    elif recommend_phq9 and recommend_gad7:
        message = "Administer both the PHQ-9 and the GAD-7 for a fuller assessment."
    elif recommend_phq9:
        message = "Administer the PHQ-9 to further evaluate depressive symptoms."
    else:
        message = "Administer the GAD-7 to further evaluate anxiety symptoms."

    return {
        "recommend_phq9": recommend_phq9,
        "recommend_gad7": recommend_gad7,
        "message": message,
    }


PHQ9_SEVERITY = [
    (0, 4, "Minimal"),
    (5, 9, "Mild"),
    (10, 14, "Moderate"),
    (15, 19, "Moderately severe"),
    (20, 27, "Severe"),
]


def score_phq9(responses: Dict[str, int]) -> Dict[str, object]:
    """Calculate PHQ-9 total and severity information."""

    expected_ids = {f"phq9_q{idx}": range(0, 4) for idx in range(1, 10)}
    _validate_responses(responses, expected_ids)

    total_score = sum(responses.values())
    item_9_score = responses["phq9_q9"]

    severity = next((label for lower, upper, label in PHQ9_SEVERITY if lower <= total_score <= upper), "Unknown")
    recommend_cssrs = item_9_score > 0 or total_score >= 10

    if recommend_cssrs:
        message = (
            "Administer the C-SSRS screener because item 9 was positive or the total score indicates elevated risk."
        )
    else:
        message = "C-SSRS screener is not required based on current PHQ-9 responses."

    return {
        "total_score": total_score,
        "item_9_score": item_9_score,
        "severity": severity,
        "recommend_cssrs": recommend_cssrs,
        "message": message,
    }


GAD7_SEVERITY = [
    (0, 4, "Minimal"),
    (5, 9, "Mild"),
    (10, 14, "Moderate"),
    (15, 21, "Severe"),
]


def score_gad7(responses: Dict[str, int]) -> Dict[str, object]:
    """Calculate GAD-7 total and severity."""

    expected_ids = {f"gad7_q{idx}": range(0, 4) for idx in range(1, 8)}
    _validate_responses(responses, expected_ids)

    total_score = sum(responses.values())
    severity = next((label for lower, upper, label in GAD7_SEVERITY if lower <= total_score <= upper), "Unknown")

    return {
        "total_score": total_score,
        "severity": severity,
    }


CSSRS_LEVELS = {
    "no_risk": {
        "label": "No indicated suicidal ideation",
        "description": "No items on the C-SSRS screener were endorsed.",
    },
    "low": {
        "label": "Suicidal ideation present",
        "description": "Client endorsed wish to be dead or suicidal thoughts without plan or intent.",
    },
    "moderate": {
        "label": "Suicidal ideation with intent or plan",
        "description": "Client endorsed suicidal thoughts with intent or specific planning.",
    },
    "high": {
        "label": "Suicidal behavior present",
        "description": "Client endorsed a suicidal behavior or attempt.",
    },
}


def evaluate_cssrs(responses: Dict[str, int]) -> Dict[str, object]:
    """Provide a simple risk categorisation for the C-SSRS screener."""

    expected_ids = {f"cssrs_q{idx}": range(0, 2) for idx in range(1, 7)}
    _validate_responses(responses, expected_ids)

    yes_responses = {qid for qid, value in responses.items() if value == 1}

    if any(qid == "cssrs_q6" for qid in yes_responses):
        level_key = "high"
    elif any(qid in {"cssrs_q4", "cssrs_q5"} for qid in yes_responses):
        level_key = "moderate"
    elif any(qid in {"cssrs_q1", "cssrs_q2", "cssrs_q3"} for qid in yes_responses):
        level_key = "low"
    else:
        level_key = "no_risk"

    level = CSSRS_LEVELS[level_key]

    return {
        "risk_level": level["label"],
        "description": level["description"],
    }


TIER_DEFINITIONS = {
    1: {
        "name": "Tier 1",
        "label": "Self-management and monitoring",
        "description": "Symptoms fall below the threshold for low intensity interventions. Continue monitoring and provide psychoeducation.",
    },
    2: {
        "name": "Tier 2",
        "label": "Low intensity services",
        "description": "Recommend guided self-help, brief interventions, or digital therapeutics.",
    },
    3: {
        "name": "Tier 3",
        "label": "Moderate intensity services",
        "description": "Recommend structured psychological therapies or psychiatric consultation.",
    },
    4: {
        "name": "Tier 4",
        "label": "High intensity services",
        "description": "Recommend specialist mental health services and multidisciplinary support.",
    },
}


def _tier_from_phq9(score: Optional[int]) -> Optional[int]:
    if score is None:
        return None
    if score >= 20:
        return 4
    if score >= 10:
        return 3
    if score >= 5:
        return 2
    return 1


def _tier_from_gad7(score: Optional[int]) -> Optional[int]:
    if score is None:
        return None
    if score >= 15:
        return 4
    if score >= 10:
        return 3
    if score >= 5:
        return 2
    return 1


def determine_tier(phq9_score: Optional[int], gad7_score: Optional[int]) -> Dict[str, object]:
    """Combine PHQ-9 and GAD-7 scores to derive a service tier."""

    phq9_tier = _tier_from_phq9(phq9_score)
    gad7_tier = _tier_from_gad7(gad7_score)

    available_tiers = [tier for tier in [phq9_tier, gad7_tier] if tier is not None]
    if not available_tiers:
        raise QuestionnaireScoringError("At least one of PHQ-9 or GAD-7 scores must be provided.")

    final_tier_level = max(available_tiers)
    tier_definition = TIER_DEFINITIONS[final_tier_level]

    breakdown = {}
    if phq9_tier is not None:
        breakdown["phq9"] = {
            "score": phq9_score,
            "tier": phq9_tier,
        }
    if gad7_tier is not None:
        breakdown["gad7"] = {
            "score": gad7_score,
            "tier": gad7_tier,
        }

    return {
        "tier": {
            "level": final_tier_level,
            "name": tier_definition["name"],
            "label": tier_definition["label"],
            "description": tier_definition["description"],
        },
        "tool_breakdown": breakdown,
    }

