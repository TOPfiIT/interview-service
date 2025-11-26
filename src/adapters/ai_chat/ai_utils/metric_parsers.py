import json
from typing import Any

from src.domain.metrics.metrics import (
    MetricsBlock2,
    MetricsBlock3,
    TechFitLevel,
    SeniorityGuess,
    Recommendation,
)


def _load_json(obj: str | dict[str, Any]) -> dict[str, Any]:
    """
    Accept either a raw JSON string or a pre-parsed dict.
    Always return a dict or raise ValueError.
    """
    if isinstance(obj, dict):
        return obj
    try:
        data = json.loads(obj)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data


def parse_metrics_block2(json_obj: str | dict[str, Any]) -> MetricsBlock2:
    """
    Parse LLM JSON into MetricsBlock2.

    Expected keys:
      - summary: str
      - clarity_score: int (0–5)
      - completeness_score: int (0–5)
      - feedback_response: str
      - tech_fit_level: "low" | "medium" | "high"
      - tech_fit_comment: str
    """
    data = _load_json(json_obj)

    required_keys = {
        "summary",
        "clarity_score",
        "completeness_score",
        "feedback_response",
        "tech_fit_level",
        "tech_fit_comment",
    }
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Missing keys in MetricsBlock2 JSON: {missing}")

    summary = str(data["summary"])
    feedback_response = str(data["feedback_response"])
    tech_fit_comment = str(data["tech_fit_comment"])

    # scores
    try:
        clarity_score = int(data["clarity_score"])
        completeness_score = int(data["completeness_score"])
    except (TypeError, ValueError) as e:
        raise ValueError("clarity_score and completeness_score must be integers") from e

    if not (0 <= clarity_score <= 5):
        raise ValueError(f"clarity_score must be in [0,5], got {clarity_score}")
    if not (0 <= completeness_score <= 5):
        raise ValueError(f"completeness_score must be in [0,5], got {completeness_score}")

    # tech_fit_level enum
    tech_fit_str = str(data["tech_fit_level"]).lower()
    try:
        tech_fit_level = TechFitLevel(tech_fit_str)
    except ValueError as e:
        valid = ", ".join(t.value for t in TechFitLevel)
        raise ValueError(
            f"Invalid tech_fit_level '{tech_fit_str}', expected one of: {valid}"
        ) from e

    return MetricsBlock2(
        summary=summary,
        clarity_score=clarity_score,
        completeness_score=completeness_score,
        feedback_response=feedback_response,
        tech_fit_level=tech_fit_level,
        tech_fit_comment=tech_fit_comment,
    )


def parse_metrics_block3(json_obj: str | dict[str, Any]) -> MetricsBlock3:
    """
    Parse LLM JSON into MetricsBlock3.

    Expected keys:
      - strengths: str
      - weaknesses: str
      - cheating_summary: str
      - seniority_guess: "junior" | "middle" | "senior"
      - recommendation: "reject" | "doubt" | "hire" | "strong_hire"
    """
    data = _load_json(json_obj)

    required_keys = {
        "strengths",
        "weaknesses",
        "cheating_summary",
        "seniority_guess",
        "recommendation",
    }
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Missing keys in MetricsBlock3 JSON: {missing}")

    strengths = str(data["strengths"])
    weaknesses = str(data["weaknesses"])
    cheating_summary = str(data["cheating_summary"])

    # seniority_guess enum
    seniority_str = str(data["seniority_guess"]).lower()
    try:
        seniority_guess = SeniorityGuess(seniority_str)
    except ValueError as e:
        valid = ", ".join(s.value for s in SeniorityGuess)
        raise ValueError(
            f"Invalid seniority_guess '{seniority_str}', expected one of: {valid}"
        ) from e

    # recommendation enum
    recommendation_str = str(data["recommendation"]).lower()
    try:
        recommendation = Recommendation(recommendation_str)
    except ValueError as e:
        valid = ", ".join(r.value for r in Recommendation)
        raise ValueError(
            f"Invalid recommendation '{recommendation_str}', expected one of: {valid}"
        ) from e

    return MetricsBlock3(
        strengths=strengths,
        weaknesses=weaknesses,
        cheating_summary=cheating_summary,
        seniority_guess=seniority_guess,
        recommendation=recommendation,
    )
