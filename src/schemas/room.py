from pydantic import BaseModel


class VacancyRoom(BaseModel):
    profession: str
    position: str


class Task(BaseModel):
    type: str
    condition: str
    language: str


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


class SendSolutionRequest(BaseModel):
    solution: str
    copy_paste_count: int
    language: str
    solution_type: str


class TaskMetadata(BaseModel):
    type: str
    language: str


class QuestionSendRequest(BaseModel):
    question: str
