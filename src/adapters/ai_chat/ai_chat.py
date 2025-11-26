import os
import asyncio
from typing import Any, AsyncGenerator, Coroutine
import dotenv
from openai import OpenAI

from src.adapters.ai_chat.ai_utils.map_enum import (
    map_user_type,
    map_assistant_type,
    map_task_language,
    map_task_type,
)
from src.core.setting import settings
from src.adapters.ai_chat.ai_utils.misc import (
    get_chat_completion_stream,
    remove_thinking_part,
)
from src.adapters.ai_chat.ai_utils.prompt_builders import (
    build_chat_plan_prompt,
    build_chat_plan_system_prompt,
    build_chat_system_prompt,
    build_response_prompts,
    build_create_task_system_prompt,
    build_create_task_user_prompt,
    build_metrics_block2_system_prompt,
    build_metrics_block2_user_prompt,
    build_metrics_block3_system_prompt,
    build_metrics_block3_user_prompt,
    build_response_system_prompt,
    build_response_user_prompt,
    build_chat_welcome_user_prompt,
)
from src.adapters.ai_chat.ai_utils.streams import strip_think_and_ctrl, filter_thinking_chunks
from src.domain.message.message import Message
from src.domain.metrics.metrics import MetricsBlock1, MetricsBlock2, MetricsBlock3
from src.domain.task.task import Task
from src.domain.vacancy.vacancy import VacancyInfo
from src.usecases.interfaces.ai_chat import AIChatBase
from src.domain.message.message import RoleEnum
from src.adapters.ai_chat.ai_utils.metric_parsers import (
    parse_metrics_block2,
    parse_metrics_block3,
)

dotenv.load_dotenv()


class AIChat(AIChatBase):
    """
    LLM-backed implementation of the interview chat, task, and metrics logic.
    """

    def __init__(self):
        """
        Initialize OpenAI-compatible client from settings.
        """
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def create_chat(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[VacancyInfo, AsyncGenerator[str, None]]:
        """
        Generate or update the INTERNAL interview plan for the vacancy.
        """
        system_prompt = build_chat_plan_system_prompt()
        plan_prompt = build_chat_plan_prompt(vacancy_info)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": plan_prompt},
        ]

        completion = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
        )
        interview_plan = completion.choices[0].message.content.strip()
        interview_plan = remove_thinking_part(interview_plan)

        updated_vacancy = vacancy_info
        updated_vacancy.interview_plan = interview_plan

        return updated_vacancy

    async def generate_welcome_message(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> AsyncGenerator[str, None]:
        """
        Stream the first welcome message, hiding any <think>...</think> content.
        """
        system_prompt = build_chat_system_prompt()
        user_prompt = build_chat_welcome_user_prompt(vacancy_info, chat_history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        stream = filter_thinking_chunks(raw_stream)
        return stream

    async def create_response(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        task: Task,
    ) -> tuple[AsyncGenerator[str, None], Message, Message]:
        """
        Stream the next interviewer reply and classify user/AI message types via <ctrl>.
        """
        system_prompt, user_prompt = build_response_prompts(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            task=task,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        # TODO: Add error handling and retry handling for strip_think_and_ctrl
        control, body_stream = strip_think_and_ctrl(raw_stream)

        user_type = map_user_type(control.get("user_type"))
        assistant_type = map_assistant_type(control.get("assistant_type"))

        user_message = Message(
            role=RoleEnum.USER,
            type=user_type,
            content="",  # filled elsewhere with actual user text
        )

        ai_message = Message(
            role=RoleEnum.AI,
            type=assistant_type,
            content="",  # will be filled from streamed body
        )

        return body_stream, user_message, ai_message

    async def create_task(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
    ) -> tuple[AsyncGenerator[str, None], Task]:
        """
        Stream the next task text and derive Task type/language from <ctrl>.
        """
        system_prompt = build_create_task_system_prompt()
        user_prompt = build_create_task_user_prompt(vacancy_info, chat_history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_stream = get_chat_completion_stream(
            self.client,
            settings.llm_model,
            messages,
        )

        # TODO: Add error handling and retry handling for strip_think_and_ctrl
        control, body_stream = strip_think_and_ctrl(raw_stream)

        task_type = map_task_type(control.get("task_type"))
        task_language = map_task_language(control.get("task_language"))

        task = Task(
            type=task_type,
            language=task_language,
            description="",  # caller can fill from streamed text
        )

        return body_stream, task

    async def create_metrics(
        self,
        vacancy_info: VacancyInfo,
        chat_history: list[Message],
        metrics_block1: MetricsBlock1,
    ) -> tuple[MetricsBlock1, MetricsBlock2, MetricsBlock3]:
        """
        Compute MetricsBlock2 and MetricsBlock3 from vacancy, chat, and MetricsBlock1.
        """
        # -------- Block 2: summary + local scores + tech fit --------
        system_prompt_b2 = build_metrics_block2_system_prompt()
        user_prompt_b2 = build_metrics_block2_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            metrics_block1=metrics_block1,
        )

        messages_b2 = [
            {"role": "system", "content": system_prompt_b2},
            {"role": "user", "content": user_prompt_b2},
        ]

        completion_b2 = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages_b2,
        )

        raw_json_b2 = completion_b2.choices[0].message.content
        metrics_block2 = parse_metrics_block2(raw_json_b2)

        # -------- Block 3: final verdict --------
        system_prompt_b3 = build_metrics_block3_system_prompt()
        user_prompt_b3 = build_metrics_block3_user_prompt(
            vacancy_info=vacancy_info,
            chat_history=chat_history,
            metrics_block1=metrics_block1,
            metrics_block2=metrics_block2,
        )

        messages_b3 = [
            {"role": "system", "content": system_prompt_b3},
            {"role": "user", "content": user_prompt_b3},
        ]

        completion_b3 = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages_b3,
        )

        raw_json_b3 = completion_b3.choices[0].message.content
        metrics_block3 = parse_metrics_block3(raw_json_b3)

        return metrics_block1, metrics_block2, metrics_block3
