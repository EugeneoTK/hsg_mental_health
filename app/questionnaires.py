"""Questionnaire definitions for the mental health tiered care calculator."""
from __future__ import annotations

from typing import Dict, List

ScaleOption = Dict[str, str]
Question = Dict[str, object]


LIKERT_OPTIONS = [
    {"value": 0, "label": "Not at all"},
    {"value": 1, "label": "Several days"},
    {"value": 2, "label": "More than half the days"},
    {"value": 3, "label": "Nearly every day"},
]

PHQ4: Dict[str, object] = {
    "id": "phq4",
    "title": "Patient Health Questionnaire-4 (PHQ-4)",
    "description": (
        "Over the last 2 weeks, how often have you been bothered by the following "
        "problems?"
    ),
    "questions": [
        {
            "id": "phq4_q1",
            "text": "Little interest or pleasure in doing things",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq4_q2",
            "text": "Feeling down, depressed, or hopeless",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq4_q3",
            "text": "Feeling nervous, anxious, or on edge",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq4_q4",
            "text": "Not being able to stop or control worrying",
            "options": LIKERT_OPTIONS,
        },
    ],
}

PHQ9: Dict[str, object] = {
    "id": "phq9",
    "title": "Patient Health Questionnaire-9 (PHQ-9)",
    "description": (
        "Over the last 2 weeks, how often have you been bothered by the following "
        "problems?"
    ),
    "questions": [
        {
            "id": "phq9_q1",
            "text": "Little interest or pleasure in doing things",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q2",
            "text": "Feeling down, depressed, or hopeless",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q3",
            "text": "Trouble falling or staying asleep, or sleeping too much",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q4",
            "text": "Feeling tired or having little energy",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q5",
            "text": "Poor appetite or overeating",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q6",
            "text": "Feeling bad about yourself—or that you are a failure or have let yourself or your family down",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q7",
            "text": "Trouble concentrating on things, such as reading the newspaper or watching television",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q8",
            "text": "Moving or speaking so slowly that other people could have noticed? Or the opposite—being so fidgety or restless that you have been moving around a lot more than usual",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "phq9_q9",
            "text": "Thoughts that you would be better off dead or of hurting yourself in some way",
            "options": LIKERT_OPTIONS,
        },
    ],
}

GAD7: Dict[str, object] = {
    "id": "gad7",
    "title": "Generalized Anxiety Disorder 7-item (GAD-7)",
    "description": (
        "Over the last 2 weeks, how often have you been bothered by the following "
        "problems?"
    ),
    "questions": [
        {
            "id": "gad7_q1",
            "text": "Feeling nervous, anxious, or on edge",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q2",
            "text": "Not being able to stop or control worrying",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q3",
            "text": "Worrying too much about different things",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q4",
            "text": "Trouble relaxing",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q5",
            "text": "Being so restless that it's hard to sit still",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q6",
            "text": "Becoming easily annoyed or irritable",
            "options": LIKERT_OPTIONS,
        },
        {
            "id": "gad7_q7",
            "text": "Feeling afraid, as if something awful might happen",
            "options": LIKERT_OPTIONS,
        },
    ],
}

CSSRS_SCREEN: Dict[str, object] = {
    "id": "cssrs",
    "title": "Columbia-Suicide Severity Rating Scale (C-SSRS) Screener",
    "description": (
        "Ask the client to respond Yes or No to each question based on the last month unless otherwise specified."
    ),
    "questions": [
        {
            "id": "cssrs_q1",
            "text": "Have you wished you were dead or wished you could go to sleep and not wake up?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
        },
        {
            "id": "cssrs_q2",
            "text": "Have you actually had any thoughts of killing yourself?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
        },
        {
            "id": "cssrs_q3",
            "text": "Have you been thinking about how you might kill yourself?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
        },
        {
            "id": "cssrs_q4",
            "text": "Have you had these thoughts and had some intention of acting on them?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
        },
        {
            "id": "cssrs_q5",
            "text": "Have you started to work out or worked out the details of how to kill yourself? Do you intend to carry out this plan?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
        },
        {
            "id": "cssrs_q6",
            "text": "Have you ever done anything, started to do anything, or prepared to do anything to end your life?",
            "options": [
                {"value": 1, "label": "Yes"},
                {"value": 0, "label": "No"},
            ],
            "note": "If yes, ask about the most recent behavior and whether it occurred within the past 3 months.",
        },
    ],
}

QUESTIONNAIRES: Dict[str, Dict[str, object]] = {
    "phq4": PHQ4,
    "phq9": PHQ9,
    "gad7": GAD7,
    "cssrs": CSSRS_SCREEN,
}


def list_questionnaires() -> List[Dict[str, object]]:
    """Return the metadata for all supported questionnaires."""
    return [QUESTIONNAIRES[key] for key in QUESTIONNAIRES]


def get_questionnaire(name: str) -> Dict[str, object]:
    """Retrieve a single questionnaire definition by its identifier."""
    key = name.lower()
    if key not in QUESTIONNAIRES:
        raise KeyError(f"Unknown questionnaire '{name}'.")
    return QUESTIONNAIRES[key]

