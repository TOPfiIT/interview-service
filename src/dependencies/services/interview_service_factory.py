from src.usecases.interfaces.vacancy_service import VacancyServiceBase
from src.usecases.interfaces.interview_service import InterviewServiceBase
from src.usecases.interfaces.ai_chat import AIChatBase
from src.dependencies.registrator import add_factory_to_mapper
from src.usecases.interview_service.service import InterviewService
from src.adapters.vacancy_service.vacancy_service import VacancyService
from src.core.setting import settings
from src.adapters.ai_chat.ai_chat import AIChat
from src.usecases.interfaces.code_run_service import CodeRunServiceBase
from src.adapters.code_run_service import CodeRunService


@add_factory_to_mapper(InterviewServiceBase)
def create_interview_service() -> InterviewServiceBase:
    vacancy_service: VacancyServiceBase = VacancyService(settings.vacancy_service_url)
    ai_chat: AIChatBase = AIChat()
    code_run_service: CodeRunServiceBase = CodeRunService(
        settings.code_run_service_url, settings.code_run_service_api_key
    )

    return InterviewService(vacancy_service, ai_chat, code_run_service)
