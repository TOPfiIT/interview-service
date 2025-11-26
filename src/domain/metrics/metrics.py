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

class SeniorityGuess(str, Enum):
    """
    Seniority guess enum
    """
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

class Recommendation(str, Enum):
    """
    Recommendation enum
    """
    REJECT = "reject"
    DOUBT = "doubt"
    HIRE = "hire"
    STRONG_HIRE = "strong_hire"

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
    clarity_score: int # 0-5
    completeness_score: int # 0-5
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

#TODO: Implement tests and code metrics