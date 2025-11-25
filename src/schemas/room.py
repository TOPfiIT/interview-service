from pydantic import BaseModel


class VacancyRoom(BaseModel):
    profession: str
    position: str


class Task(BaseModel):
    type: str
    condition: str


class Message(BaseModel):
    sender: str
    content: str


class InterviewRoom(BaseModel):
    vacancy: VacancyRoom
    tasks: list[Task]
    chat: list[Message]


class SolutionSentResponse(BaseModel):
    new_task: Task


class QuestionSentResponse(BaseModel):
    response: str
