from typing import Dict, Any
from src.domain.message.message import Message, RoleEnum, TypeEnum


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
