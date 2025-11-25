from pydantic import BaseModel


class CreatedRoomRequest(BaseModel):
    vacancy_id: str
    name: str
    surname: str
    resume_link: str
