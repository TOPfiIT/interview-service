from dataclasses import dataclass
from datetime import timedelta
from enum import Enum


class TechFitLevel(str, Enum):
    """
    Tech fit level enum
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


class SeniorityGuess(str, Enum):
    """
    Seniority guess enum
    """

    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


class Recommendation(str, Enum):
    """
    Recommendation enum
    """

    REJECT = "reject"
    DOUBT = "doubt"
    HIRE = "hire"
    STRONG_HIRE = "strong_hire"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


@dataclass
class MetricsBlock1:
    """
    Metrics class
    """

    time_spent: timedelta
    time_per_task: timedelta
    answers_count: int
    copy_paste_suspicion: int


@dataclass
class MetricsBlock2:
    """
    Metrics class
    """

    summary: str
    clarity_score: int  # 0-5
    completeness_score: int  # 0-5
    feedback_response: str
    tech_fit_level: TechFitLevel
    tech_fit_comment: str


@dataclass
class MetricsBlock3:
    """
    Metrics class
    """

    strengths: str
    weaknesses: str
    cheating_summary: str
    seniority_guess: SeniorityGuess
    recommendation: Recommendation


@dataclass
class CodeTestMetrics:
    """
    Metrics for code execution and test results during the interview.
    All fields are simple counters, aggregated over the whole session.
    """

    passed_tests: int = 0  # Number of tests passed
    failed_tests: int = 0  # Number of tests failed
    compile_errors: int = 0  # Number of compilation / syntax error runs
    runtime_errors: int = 0  # Number of runtime-error runs
    attempts_count: int = 0  # How many times the user ran the code

