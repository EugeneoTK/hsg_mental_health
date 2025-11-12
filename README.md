# hsg_mental_health

Developing SG Mental Health Tiered Care logic and Front-end Calculator.

## Overview

This project implements the decision flow for administering PHQ-4, PHQ-9, GAD-7, and the C-SSRS
screener, and combines the results to recommend a tier of mental health support. It consists of a
FastAPI backend that scores the questionnaires and a browser-based front-end that guides users
through the screening steps.

## Getting started

1. Create a virtual environment and install the dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Open <http://127.0.0.1:8000> in your browser to access the calculator.

The API is documented via the interactive OpenAPI schema at
<http://127.0.0.1:8000/docs>.

## API Summary

The API is designed to be modular. Each questionnaire can be scored independently using the
following endpoints:

- `POST /api/assessments/phq4` — accepts PHQ-4 item scores and recommends whether to administer the PHQ-9 and/or GAD-7.
- `POST /api/assessments/phq9` — returns PHQ-9 totals, severity, and whether the C-SSRS should be administered.
- `POST /api/assessments/gad7` — calculates the GAD-7 total and severity.
- `POST /api/assessments/cssrs` — summarises suicide risk from the C-SSRS screener items.
- `POST /api/assessments/tier` — determines the service tier by combining PHQ-9 and GAD-7 scores.

Question metadata (including question text and scoring options) is available via
`GET /api/questionnaires` and `GET /api/questionnaires/{name}`.

## Front-end Flow

The front-end lives at `static/index.html` and progressively reveals each assessment based on API
responses. It displays questionnaire results, risk messaging, and the recommended tier of care.
