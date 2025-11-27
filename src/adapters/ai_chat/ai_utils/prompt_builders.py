from datetime import timedelta
from typing import Any
from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.metrics.metrics import MetricsBlock1, MetricsBlock2
from src.domain.task.task import Task, TaskType, TaskLanguage
from src.domain.vacancy.vacancy import VacancyInfo
from src.adapters.ai_chat.ai_utils.prompt_utils import load_prompt
from src.domain.test.test import CodeTestSuite


def _format_chat_history(chat_history: list[Message]) -> str:
    """
    Format chat history into a plain-text transcript for the LLM.
    """
    lines: list[str] = []

    for msg in chat_history:
        if msg.role == RoleEnum.USER:
            role_label = "Candidate"
        else:
            role_label = "Interviewer"

        lines.append(f"{role_label} [{msg.type.value}]: {msg.content}")

    return "\n".join(lines)


# ---------- RESPONSE ----------

def build_response_system_prompt() -> str:
    return load_prompt("system/response_system_prompt.txt")


def build_response_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    task: Task,
) -> str:
    template = load_prompt("user/response_prompt.txt")

    vacancy_str = str(vacancy_info)
    chat_history_str = _format_chat_history(chat_history)

    task_type = task.type.value
    task_language = task.language or "not specified"
    task_description = task.description

    return template.format(
        vacancy_info=vacancy_str,
        chat_history=chat_history_str,
        task_type=task_type,
        task_language=task_language,
        task_description=task_description,
    )


def build_response_prompts(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    task: Task,
) -> tuple[str, str]:
    system_prompt = build_response_system_prompt()
    user_prompt = build_response_user_prompt(vacancy_info, chat_history, task)
    return system_prompt, user_prompt


# ---------- CHAT PLAN ----------

def build_chat_plan_system_prompt() -> str:
    """
    Load the static system prompt for interview plan generation.
    """
    return load_prompt("system/create_chat_plan_system_prompt.txt")


def build_chat_plan_prompt(vacancy_info: VacancyInfo) -> str:
    """
    Build the user prompt that asks the LLM to generate or update
    VacancyInfo.interview_plan based on the vacancy fields, tasks, and duration.
    """
    template = load_prompt("user/create_chat_plan_prompt.txt")

    tasks_str = "\n".join(f"- {t}" for t in vacancy_info.tasks) if vacancy_info.tasks else "(none)"
    task_ideas_str = "\n".join(f"- {t}" for t in vacancy_info.task_ides) if vacancy_info.task_ides else "(none)"
    existing_plan = vacancy_info.interview_plan or ""

    # Convert duration to minutes (int). Fall back to 30 if duration is somehow not set.
    if isinstance(vacancy_info.duration, timedelta):
        duration_minutes = max(1, int(vacancy_info.duration.total_seconds() // 60) or 1)
    else:
        duration_minutes = 90

    return template.format(
        profession=vacancy_info.profession,
        position=vacancy_info.position,
        requirements=vacancy_info.requirements,
        questions=vacancy_info.questions,
        tasks=tasks_str,
        task_ideas=task_ideas_str,
        interview_plan=existing_plan,
        duration_minutes=duration_minutes,
    )



# ---------- CHAT WELCOME ----------

def build_chat_welcome_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
) -> str:
    template = load_prompt("user/chat_welcome_prompt.txt")

    vacancy_str = str(vacancy_info)
    chat_history_str = _format_chat_history(chat_history)
    interview_plan = vacancy_info.interview_plan or "(no plan generated yet)"

    return template.format(
        vacancy_info=vacancy_str,
        interview_plan=interview_plan,
        chat_history=chat_history_str,
    )


def build_chat_system_prompt() -> str:
    return load_prompt("system/chat_welcome_system_prompt.txt")


# ---------- CREATE TASK ----------

def build_create_task_system_prompt() -> str:
    return load_prompt("system/create_task_system_prompt.txt")


def build_create_task_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
) -> str:
    template = load_prompt("user/create_task_prompt.txt")

    vacancy_str = str(vacancy_info)
    plan = vacancy_info.interview_plan or ""
    history_str = _format_chat_history(chat_history)

    # adaptive language list from enum
    supported_languages = ", ".join(lang.value for lang in TaskLanguage) if TaskLanguage else "(none)"

    return template.format(
        vacancy_info=vacancy_str,
        interview_plan=plan,
        chat_history=history_str,
        supported_languages=supported_languages,
    )


# ---------- CREATE METRICS ----------


def _format_metrics_block1(m: MetricsBlock1) -> str:
    """
    Serialize MetricsBlock1 into a compact, LLM-friendly text snippet.
    Timedeltas are converted to integer seconds.
    """
    time_spent_sec = int(m.time_spent.total_seconds())
    time_per_task_sec = int(m.time_per_task.total_seconds())

    # Keep it plain text, easy to read
    return (
        f"time_spent_seconds: {time_spent_sec}\n"
        f"time_per_task_seconds: {time_per_task_sec}\n"
        f"answers_count: {m.answers_count}\n"
        f"copy_paste_suspicion: {m.copy_paste_suspicion}"
    )

def _format_metrics_block2(m: MetricsBlock2) -> str:
    """
    Serialize MetricsBlock2 into a compact, LLM-friendly text snippet.
    """
    return (
        f"summary: {m.summary}\n"
        f"clarity_score: {m.clarity_score}\n"
        f"completeness_score: {m.completeness_score}\n"
        f"feedback_response: {m.feedback_response}\n"
        f"tech_fit_level: {m.tech_fit_level.value}\n"
        f"tech_fit_comment: {m.tech_fit_comment}"
    )


def build_metrics_block2_system_prompt() -> str:
    """
    Load the static system prompt for MetricsBlock2 generation.
    """
    return load_prompt("system/metrics_block2_system_prompt.txt")


def build_metrics_block2_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    metrics_block1: MetricsBlock1,
) -> str:
    """
    Build the dynamic user prompt for MetricsBlock2 generation.
    """
    template = load_prompt("user/metrics_block2_prompt.txt")

    vacancy_str = str(vacancy_info)
    history_str = _format_chat_history(chat_history)
    metrics_block1_str = _format_metrics_block1(metrics_block1)

    return template.format(
        vacancy_info=vacancy_str,
        metrics_block1=metrics_block1_str,
        chat_history=history_str,
    )

def build_metrics_block3_system_prompt() -> str:
    """
    Load the static system prompt for MetricsBlock3 generation.
    """
    return load_prompt("system/metrics_block3_system_prompt.txt")


def build_metrics_block3_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    metrics_block1: MetricsBlock1,
    metrics_block2: MetricsBlock2,
) -> str:
    """
    Build the dynamic user prompt for MetricsBlock3 generation.
    """
    template = load_prompt("user/metrics_block3_prompt.txt")

    vacancy_str = str(vacancy_info)
    history_str = _format_chat_history(chat_history)
    block1_str = _format_metrics_block1(metrics_block1)
    block2_str = _format_metrics_block2(metrics_block2)

    return template.format(
        vacancy_info=vacancy_str,
        metrics_block1=block1_str,
        metrics_block2=block2_str,
        chat_history=history_str,
    )


if __name__ == "__main__":
    print(build_response_system_prompt())
    response_user_prompt = build_response_user_prompt(
        VacancyInfo(
            profession="AI Developer",
            position="AI Developer",
            requirements="AI Developer",
            questions="AI Developer",
            tasks=["AI Developer"],
            task_ides=["AI Developer"],
            interview_plan="",
        ),
        [Message(role=RoleEnum.USER, type=TypeEnum.QUESTION, content="Hello, how are you?")],
        Task(type=TaskType.THEORY, language=None, description="Write a theory for the task"),
    )
    print(response_user_prompt)

# ---------- CREATE TEST SUITE ----------

def build_test_suite_system_prompt() -> str:
    """
    Load the static system prompt for test suite generation.
    """
    return load_prompt("system/create_test_suite_system_prompt.txt")


def build_test_suite_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    task: Task,
    total_tests: int,
) -> str:
    """
    Build the dynamic user prompt for test suite generation.

    :param vacancy_info: vacancy context (role, stack, etc.)
    :param chat_history: full chat between interviewer and candidate
    :param task: current coding task (TaskType.CODE expected)
    :param total_tests: total number of tests N the model must generate
    """
    template = load_prompt("user/create_test_suite_prompt.txt")

    vacancy_str = str(vacancy_info)
    history_str = _format_chat_history(chat_history)

    task_type = task.type.value
    task_language = task.language.value if getattr(task, "language", None) else "python"
    task_description = task.description

    return template.format(
        vacancy_info=vacancy_str,
        chat_history=history_str,
        task_type=task_type,
        task_language=task_language,
        task_description=task_description,
        total_tests=total_tests,
    )

# ---------- CHECK SOLUTION ----------

def _format_test_suite(suite: CodeTestSuite) -> str:
    """
    Serialize CodeTestSuite into a compact, LLM-friendly text snippet.

    Hidden tests are still fully shown here (server-side),
    but the model is instructed not to reveal their details to the candidate.
    """
    lines: list[str] = []

    total = len(suite.tests)
    visible = sum(1 for t in suite.tests if not t.is_hidden)
    hidden = total - visible

    lines.append(f"total_tests: {total}")
    lines.append(f"visible_tests: {visible}")
    lines.append(f"hidden_tests: {hidden}")
    lines.append("tests:")

    for case in suite.tests:
        # helper for optional fields
        def _opt(value: Any) -> str:
            return "(none)" if value is None else str(value)

        lines.append(f"- id: {case.id}")
        lines.append(f"  is_hidden: {case.is_hidden}")
        lines.append(f"  status: {_opt(getattr(case, 'status', None))}")
        lines.append(f"  correct: {_opt(case.correct)}")
        lines.append("  input:")
        lines.append("    " + "\n    ".join(case.input_data.splitlines() or ["(empty)"]))
        lines.append("  expected_output:")
        lines.append("    " + "\n    ".join(case.expected_output.splitlines() or ["(empty)"]))
        lines.append("  stdout:")
        lines.append("    " + "\n    ".join(_opt(getattr(case, 'stdout', None)).splitlines() or ["(none)"]))
        lines.append("  stderr:")
        lines.append("    " + "\n    ".join(_opt(getattr(case, 'stderr', None)).splitlines() or ["(none)"]))
        lines.append("  exception:")
        lines.append("    " + "\n    ".join(_opt(getattr(case, 'exception', None)).splitlines() or ["(none)"]))
        lines.append(f"  execution_time_ms: {_opt(getattr(case, 'execution_time', None))}")

    return "\n".join(lines)

def _format_test_suite_for_prompt(suite: CodeTestSuite) -> str:
    """
    Serialize CodeTestSuite into a compact, readable text snippet for the LLM.
    Includes test results (status, stdout, stderr, correct, visibility).
    """
    lines: list[str] = [f"task_id: {suite.task_id}", "tests:"]
    for t in suite.tests:
        visibility = "hidden" if t.is_hidden else "visible"
        lines.append(
            f"- id={t.id}; visibility={visibility}; "
            f"input={repr(t.input_data)}; "
            f"expected_output={repr(t.expected_output)}; "
            f"correct={t.correct}; "
            f"status={getattr(t, 'status', None)}; "
            f"stdout={repr(getattr(t, 'stdout', None))}; "
            f"stderr={repr(getattr(t, 'stderr', None))}"
        )
    return "\n".join(lines)


def build_check_solution_system_prompt() -> str:
    """
    Load the static system prompt for solution checking.
    """
    return load_prompt("system/check_solution_system_prompt.txt")


def build_check_solution_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    task: Task,
    solution: str,
    tests: CodeTestSuite,
) -> str:
    """
    Build the dynamic user prompt for solution checking.

    Must match placeholders in `check_solution_prompt.txt`:
      {vacancy_info}, {task_type}, {task_language},
      {task_description}, {solution}, {test_suite}, {chat_history}
    """
    template = load_prompt("user/check_solution_prompt.txt")

    vacancy_str = str(vacancy_info)
    history_str = _format_chat_history(chat_history)

    task_type = task.type.value if getattr(task, "type", None) else "unknown"
    task_language = (
        task.language.value
        if getattr(task, "language", None)
        else "not_specified"
    )

    test_suite_str = _format_test_suite_for_prompt(tests)

    return template.format(
        vacancy_info=vacancy_str,
        task_type=task_type,
        task_language=task_language,
        task_description=task.description,
        solution=solution,
        test_suite=test_suite_str,
        chat_history=history_str,
    )