from pydantic import BaseModel
from typing import Optional

class UserList(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None

    class Config:
        orm_mode = True