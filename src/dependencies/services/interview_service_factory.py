from src.usecases.interfaces.vacancy_service import VacancyServiceBase
from src.usecases.interfaces.interview_service import InterviewServiceBase
from src.usecases.interfaces.ai_chat import AIChatBase
from src.dependencies.registrator import add_factory_to_mapper
from src.usecases.interview_service.service import InterviewService
from src.adapters.vacancy_service.mock import MockVacancyService
from src.adapters.ai_chat.ai_chat import AIChat


@add_factory_to_mapper(InterviewServiceBase)
def create_interview_service() -> InterviewServiceBase:
    vacancy_service: VacancyServiceBase = MockVacancyService()
    ai_chat: AIChatBase = AIChat()

    return InterviewService(vacancy_service, ai_chat)
