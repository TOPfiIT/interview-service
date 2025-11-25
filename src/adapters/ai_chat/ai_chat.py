from src.domain.message.message import Message
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo
from src.usecases.interfaces.ai_chat import AIChatBase

from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()


class AIChat(AIChatBase):
    """
    AI Chat implementation
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

    def create_chat(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> tuple[str, Task]:
        pass

    def create_response(self, vacancy_info: VacancyInfo, chat_history: list[Message], task: Task) -> str:
        pass

if __name__ == "__main__":
    ai_chat = AIChat()
    ai_chat.create_chat(VacancyInfo(profession="Программист", position="Программист", requirements="Программист", questions="Программист", tasks=["Программист"], task_ides=["Программист"]), [])