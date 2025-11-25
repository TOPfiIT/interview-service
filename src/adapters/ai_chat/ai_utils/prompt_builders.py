from typing import List, Tuple
from src.domain.message.message import Message, RoleEnum
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo
from src.adapters.ai_chat.ai_utils.prompt_utils import load_prompt
from src.domain.task.task import TaskType
from src.domain.message.message import TypeEnum


def _format_chat_history(chat_history: List[Message]) -> str:
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
    chat_history: List[Message],
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
    chat_history: List[Message],
    task: Task,
) -> Tuple[str, str]:
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