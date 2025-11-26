from dataclasses import dataclass
from enum import Enum
from src.domain.message.message import Message, RoleEnum, TypeEnum


class TaskType(str, Enum):
    CODE = "code"
    THEORY = "theory"

class TaskLanguage(str, Enum):
    """
    Task language enum
    """
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    GO = "go"

@dataclass
class TaskMetadata:
    """
    Task metadata class
    """

    type: TaskType
    language: TaskLanguage | None


@dataclass
class Task(TaskMetadata):
    """
    Task class
    """

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
