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

    def time_spent_str(self) -> str:
        """
        Return a string representation of the time spent.
        """
        return f"Собеседование продолжалось {self.time_spent.total_seconds() // 60} мин"

    def time_per_task_str(self) -> str:
        """
        Return a string representation of the time per task.
        """
        return f"Время на одно задание: {self.time_per_task.total_seconds() // 60} мин"

    def answers_count_str(self) -> str:
        """
        Return a string representation of the answers count.
        """
        return f"Ответов: {self.answers_count}"

    def copy_paste_suspicion_str(self) -> str:
        """
        Return a string representation of the copy-paste suspicion.
        """
        return f"Подозрение в копировании: {self.copy_paste_suspicion}"


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

    def summary_str(self) -> str:
        """
        Return a string representation of the summary.
        """
        return f"Резюме: {self.summary}"

    def clarity_score_str(self) -> str:
        """
        Return a string representation of the clarity score.
        """
        return f"Оценка ясности: {self.clarity_score}"

    def completeness_score_str(self) -> str:
        """
        Return a string representation of the completeness score.
        """
        return f"Оценка полноты: {self.completeness_score}"

    def feedback_response_str(self) -> str:
        """
        Return a string representation of the feedback response.
        """
        return f"Ответ на отзыв: {self.feedback_response}"

    def tech_fit_level_str(self) -> str:
        """
        Return a string representation of the tech fit level.
        """
        return f"Уровень компетентности: {self.tech_fit_level}"

    def tech_fit_comment_str(self) -> str:
        """
        Return a string representation of the tech fit comment.
        """
        return f"Комментарий к компетентности: {self.tech_fit_comment}"


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

    def strengths_str(self) -> str:
        """
        Return a string representation of the strengths.
        """
        return f"Сильные стороны: {self.strengths}"

    def weaknesses_str(self) -> str:
        """
        Return a string representation of the weaknesses.
        """
        return f"Слабые стороны: {self.weaknesses}"

    def cheating_summary_str(self) -> str:
        """
        Return a string representation of the cheating summary.
        """
        return f"Резюме о честности собеседования: {self.cheating_summary}"

    def seniority_guess_str(self) -> str:
        """
        Return a string representation of the seniority guess.
        """
        return f"Предположение о позиции в карьере: {self.seniority_guess}"

    def recommendation_str(self) -> str:
        """
        Return a string representation of the recommendation.
        """
        return f"Рекомендация: {self.recommendation}"


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
