from typing import Dict, Any
from src.domain.message.message import Message, RoleEnum, TypeEnum
from src.domain.task.task import TaskLanguage, TaskType


def map_user_type(user_type: str | None) -> TypeEnum:
    """
    Map control['user_type'] to TypeEnum for the USER side.
    """
    match (user_type or "").lower():
        case "question":
            return TypeEnum.QUESTION
        case "answer":
            return TypeEnum.ANSWER
        case "solution":
            return TypeEnum.SOLUTION
        case "other":
            return TypeEnum.OTHER
        case _:
            # for anything unknown
            return TypeEnum.OTHER


def map_assistant_type(assistant_type: str | None) -> TypeEnum:
    """
    Map control['assistant_type'] to TypeEnum for the AI side.
    """
    match (assistant_type or "").lower():
        case "hint":
            return TypeEnum.HINT
        case "check_solution":
            return TypeEnum.CHECK_SOLUTION
        case "response":
            return TypeEnum.RESPONSE
        case _:
            # safe default
            return TypeEnum.RESPONSE

def map_task_language(task_language: str | None) -> TaskLanguage:
    """
    Map control['task_language'] to TaskLanguage.
    """
    match (task_language or "").lower():
        case "python":
            return TaskLanguage.PYTHON
        case "javascript":
            return TaskLanguage.JAVASCRIPT
        case "java":
            return TaskLanguage.JAVA
        case "c":
            return TaskLanguage.C
        case "cpp":
            return TaskLanguage.CPP
        case "csharp":
            return TaskLanguage.CSHARP
        case "php":
            return TaskLanguage.PHP
        case "ruby":
            return TaskLanguage.RUBY
        case "go":
            return TaskLanguage.GO
        case _:
            return None

def map_task_type(task_type: str | None) -> TaskType:
    """
    Map control['task_type'] to TaskType.
    Defaults to THEORY if something goes wrong.
    """
    match (task_type or "").lower():
        case "code":
            return TaskType.CODE
        case "theory":
            return TaskType.THEORY
        case _:
            return TaskType.THEORY