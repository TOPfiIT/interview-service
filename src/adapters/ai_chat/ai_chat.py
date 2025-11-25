from src.adapters.ai_chat.ai_utils.misc import get_chat_completion_stream
from src.adapters.ai_chat.ai_utils.prompt_builders import build_response_prompts
from src.domain.message.message import Message
from src.domain.metrics.metrics import Metrics
from src.domain.task.task import Task, TaskType
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

    async def create_chat(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> tuple[str, Task]:
        ...

    async def create_response(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> str:
        system_prompt, user_prompt = build_response_prompts(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        stream = get_chat_completion_stream(self.client, "qwen3-32b-awq", messages, 20000)
        inside_think = False
        for chunk in stream:
            # Check if the first chunk is <think>
            if chunk == "<think>":
                inside_think = True
                yield "Thinking...\n"
                continue

            # Check if the last chunk is </think>
            if chunk == "</think>":
                inside_think = False
                yield "Finished thinking."
                continue
            
            # If we are inside <think>, skip the chunk
            if inside_think:
                continue

            yield chunk

    
    async def create_task(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Task:
        ...
        return Task(type=TaskType.THEORY, language=None, description="Напиши теорию для решения задачи")
    
    async def create_metrics(self, vacancy_info: VacancyInfo, chat_history: list[Message]) -> Metrics:
        ...
        return Metrics(accuracy=0.9, precision=0.9, recall=0.9, f1_score=0.9)

if __name__ == "__main__":
    ai_chat = AIChat()
    ai_chat.create_chat(VacancyInfo(profession="Программист", position="Программист", requirements="Программист", questions="Программист", tasks=["Программист"], task_ides=["Программист"]), [])