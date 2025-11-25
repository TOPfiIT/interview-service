from dataclasses import dataclass
from enum import Enum
from src.domain.message.message import Message, RoleEnum, TypeEnum


class TaskType(str, Enum):
    CODE = "code"
    THEORY = "theory"


@dataclass
class Task:
    """
    Task class
    """

    type: TaskType
    language: str | None
    description: str

    def to_message(self) -> Message:
        """
        Convert task to message
        """

        return Message(
            role=RoleEnum.AI,
            type=TypeEnum.TASK,
            content=self.description,
        )
