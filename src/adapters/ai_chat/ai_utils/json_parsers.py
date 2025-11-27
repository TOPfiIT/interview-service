import json
import re
from typing import Any

from src.domain.metrics.metrics import (
    MetricsBlock2,
    MetricsBlock3,
    TechFitLevel,
    SeniorityGuess,
    Recommendation,
)
from src.domain.test.test import CodeTestCase, CodeTestSuite


def _strip_markdown_fences(s: str) -> str:
    """
    Remove ``` / ```json fences if the model wrapped JSON in markdown.
    """
    s = s.strip()
    if s.startswith("```"):
        # Drop the first line (``` or ```json)
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1 :]
        # Drop trailing ``` if present
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


def _load_json(obj: str | dict[str, Any]) -> dict[str, Any]:
    """
    Robust JSON loader:
    - Accepts dict and returns it as-is.
    - For str:
      * strips markdown fences,
      * first tries json.loads directly,
      * if that fails, extracts the first {...} block with regex and parses it.
    """
    if isinstance(obj, dict):
        return obj
    if not isinstance(obj, str):
        raise TypeError(f"Expected str or dict, got {type(obj)}")

    s = _strip_markdown_fences(obj)

    if not s:
        raise ValueError("Invalid JSON: empty string from model")

    # First attempt: parse as-is
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        # Fallback: extract first { ... } block
        match = re.search(r"\{.*\}", s, re.S)
        if not match:
            preview = s[:120].replace("\n", "\\n")
            raise ValueError(f"Invalid JSON: could not find JSON object in: '{preview}...'")
        inner = match.group(0)
        data = json.loads(inner)

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

    tech_fit_str = str(data["tech_fit_level"]).lower()
    if tech_fit_str not in {"low", "medium", "high"}:
        raise ValueError(f"Invalid tech_fit_level: {tech_fit_str}")

    return MetricsBlock2(
        summary=str(data["summary"]),
        clarity_score=int(data["clarity_score"]),
        completeness_score=int(data["completeness_score"]),
        feedback_response=str(data["feedback_response"]),
        tech_fit_level=TechFitLevel(tech_fit_str),
        tech_fit_comment=str(data["tech_fit_comment"]),
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

    seniority_str = str(data["seniority_guess"]).lower()
    if seniority_str not in {"junior", "middle", "senior"}:
        raise ValueError(f"Invalid seniority_guess: {seniority_str}")

    recommendation_str = str(data["recommendation"]).lower()
    if recommendation_str not in {"reject", "doubt", "hire", "strong_hire"}:
        raise ValueError(f"Invalid recommendation: {recommendation_str}")

    return MetricsBlock3(
        strengths=str(data["strengths"]),
        weaknesses=str(data["weaknesses"]),
        cheating_summary=str(data["cheating_summary"]),
        seniority_guess=SeniorityGuess(seniority_str),
        recommendation=Recommendation(recommendation_str),
    )


def parse_test_suite_json(
    json_obj: str | dict[str, Any],
    task_id: str,
) -> CodeTestSuite:
    """
    Parse LLM JSON into CodeTestSuite.

    Expected top-level shape:

      {
        "tests": [
          {
            "id": "t1",
            "input_data": "stdin string",
            "expected_output": "stdout string",
            "is_hidden": false
          },
          ...
        ]
      }

    Notes:
    - "id" is required, but if missing we auto-generate "t1", "t2", ...
    - "is_hidden" defaults to False if missing, and is normalized to bool
      (accepts true/false/1/0/yes/no as strings).
    """

    data = _load_json(json_obj)

    # Ensure we have tests array
    if "tests" not in data or not isinstance(data["tests"], list):
        raise ValueError("Test suite JSON must contain a 'tests' array")

    raw_tests = data["tests"]
    if not raw_tests:
        raise ValueError("Test suite JSON contains an empty 'tests' list")

    tests: list[CodeTestCase] = []

    for i, t in enumerate(raw_tests):
        if not isinstance(t, dict):
            raise ValueError(f"Test #{i} must be a JSON object, got {type(t)}")

        # id
        test_id = t.get("id")
        if not test_id:
            test_id = f"t{i + 1}"
        test_id = str(test_id)

        # input / output as strings
        input_data = str(t.get("input_data", ""))
        expected_output = str(t.get("expected_output", ""))

        # is_hidden normalization
        raw_hidden = t.get("is_hidden", False)
        if isinstance(raw_hidden, str):
            val = raw_hidden.strip().lower()
            if val in {"true", "1", "yes"}:
                is_hidden = True
            elif val in {"false", "0", "no"}:
                is_hidden = False
            else:
                raise ValueError(f"Invalid is_hidden value in test '{test_id}': {raw_hidden}")
        else:
            is_hidden = bool(raw_hidden)

        tests.append(
            CodeTestCase(
                id=test_id,
                input_data=input_data,
                expected_output=expected_output,
                is_hidden=is_hidden,
            )
        )

    return CodeTestSuite(task_id=task_id, tests=tests)