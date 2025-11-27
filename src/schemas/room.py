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


class RunCodeRequest(BaseModel):
    code: str
    language: str


class CodeRunResponse(BaseModel):
    input_data: str
    expected_output: str

    correct: bool = False

    status: str | None = None
    exception: str | None = None
    stdin: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    execution_time: int | None = None
