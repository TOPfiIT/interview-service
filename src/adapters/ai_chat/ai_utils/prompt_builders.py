from datetime import timedelta
from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.metrics.metrics import MetricsBlock1, MetricsBlock2
from src.domain.task.task import Task, TaskType, TaskLanguage
from src.domain.vacancy.vacancy import VacancyInfo
from src.adapters.ai_chat.ai_utils.prompt_utils import load_prompt


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
