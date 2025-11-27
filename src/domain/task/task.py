from dataclasses import dataclass
from enum import Enum
from src.domain.message.message import Message, RoleEnum, TypeEnum


class TaskType(str, Enum):
    CODE = "code"
    THEORY = "theory"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


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

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other


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
