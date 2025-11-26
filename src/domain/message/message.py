from dataclasses import dataclass
from enum import Enum


class TypeEnum(str, Enum):
    QUESTION = "question"
    ANSWER = "answer"
    HINT = "hint"
    CHECK_SOLUTION = "check_solution"
    RESPONSE = "response"
    OTHER = "other"
    TASK = "task"
    SOLUTION = "solution"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


class RoleEnum(str, Enum):
    USER = "user"
    AI = "ai"

    def __str__(self):
        return self.value


@dataclass
class Message:
    """
    Message class
    """

    role: RoleEnum
    type: TypeEnum
    content: str
