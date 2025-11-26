from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.task.task import Task, TaskType, TaskLanguage
from src.domain.vacancy.vacancy import VacancyInfo
from src.adapters.ai_chat.ai_utils.prompt_utils import load_prompt


def _format_chat_history(chat_history: list[Message]) -> str:
    lines: list[str] = []
    for msg in chat_history:
        role_label = "Candidate" if msg.role == RoleEnum.USER else "Interviewer"
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

def build_chat_plan_prompt(vacancy_info: VacancyInfo) -> str:
    template = load_prompt("user/create_chat_plan_prompt.txt")

    tasks_str = "\n".join(f"- {t}" for t in vacancy_info.tasks) if vacancy_info.tasks else "(none)"
    task_ideas_str = "\n".join(f"- {t}" for t in vacancy_info.task_ides) if vacancy_info.task_ides else "(none)"
    existing_plan = vacancy_info.interview_plan or ""

    return template.format(
        profession=vacancy_info.profession,
        position=vacancy_info.position,
        requirements=vacancy_info.requirements,
        questions=vacancy_info.questions,
        tasks=tasks_str,
        task_ideas=task_ideas_str,
        interview_plan=existing_plan,
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


# ---------- STREAM TASK ----------

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
