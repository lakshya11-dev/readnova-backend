
from pydantic import BaseModel, Field


class GoogleLoginRequest(BaseModel):

    id_token: str = Field(min_length=1)
