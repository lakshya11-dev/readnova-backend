from pydantic import BaseModel, EmailStr, ConfigDict


class UserResponse(BaseModel):

    id: int

    name: str

    email: EmailStr

    role: str

    is_active: bool

    model_config = ConfigDict(from_attributes=True)