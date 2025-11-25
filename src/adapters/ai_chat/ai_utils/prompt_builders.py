from src.domain.message.message import Message, RoleEnum
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo
from src.adapters.ai_chat.ai_utils.prompt_utils import load_prompt
from src.domain.task.task import TaskType
from src.domain.message.message import TypeEnum


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


def build_response_system_prompt() -> str:
    """
    Load the static system prompt for the interviewer.
    There are no dynamic fields here.
    """
    return load_prompt("response_system_prompt.txt")

def build_response_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
    task: Task,
) -> str:
    """
    Build the user prompt (dynamic) for the interviewer.
    """

    template = load_prompt("response_prompt.txt")

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
    """
    Convenience wrapper that returns (system_prompt, user_prompt)
    """

    system_prompt = build_response_system_prompt()
    user_prompt = build_response_user_prompt(
        vacancy_info=vacancy_info,
        chat_history=chat_history,
        task=task,
    )

    return system_prompt, user_prompt

def build_chat_plan_prompt(vacancy_info: VacancyInfo) -> str:
    """
    Build the prompt that asks the LLM to generate or update
    VacancyInfo.interview_plan based on the vacancy fields and tasks.
    """

    template = load_prompt("create_chat_plan_prompt.txt")

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


def build_chat_welcome_user_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
) -> str:
    """
    Build the user prompt for the first welcome message in create_chat().
    """

    template = load_prompt("chat_welcome_prompt.txt")

    vacancy_str = str(vacancy_info)  # or format manually if you prefer
    chat_history_str = _format_chat_history(chat_history)
    interview_plan = vacancy_info.interview_plan or "(no plan generated yet)"

    return template.format(
        vacancy_info=vacancy_str,
        interview_plan=interview_plan,
        chat_history=chat_history_str,
    )


def build_chat_system_prompt() -> str:
    """
    Load the static system prompt for the chat initialization (create_chat).

    This defines the global behavior of the AI Interviewer when
    generating the welcome message and conducting the interview.
    """
    return load_prompt("chat_welcome_system_prompt.txt")

def build_stream_task_prompt(
    vacancy_info: VacancyInfo,
    chat_history: list[Message],
) -> str:
    """
    Build the prompt for streaming the next task description.
    The model will select the next task from the interview_plan and
    output a tagged description ([coding]/[theory], and language for coding).
    """
    template = load_prompt("create_task_prompt.txt")

    vacancy_str = str(vacancy_info)
    plan = vacancy_info.interview_plan or ""
    history_str = _format_chat_history(chat_history)

    return template.format(
        vacancy_info=vacancy_str,
        interview_plan=plan,
        chat_history=history_str,
    )

if __name__ == "__main__":
    print(build_response_system_prompt())
    response_user_prompt = build_response_user_prompt(
        VacancyInfo(profession="AI Developer", position="AI Developer",
        requirements="AI Developer", questions="AI Developer", tasks=["AI Developer"], task_ides=["AI Developer"], interview_plan=""),
        [Message(role=RoleEnum.USER, type=TypeEnum.QUESTION, content="Hello, how are you?")],
        Task(type=TaskType.THEORY, language=None, description="Write a theory for the task")
    )
    response_system_prompt = build_response_system_prompt()
    print(response_system_prompt)
    print(response_user_prompt)