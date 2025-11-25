from src.domain.message.message import Message
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo
from src.usecases.interfaces.ai_chat import AIChatBase

from openai import OpenAI
import os

class AIChat(AIChatBase):
    """
    AI Chat implementation
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def create_chat(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> tuple[str, Task]:
        pass

    def create_response(self, vacancy_info: VacancyInfo, chat_history: list[Message], task: Task) -> str:
        pass