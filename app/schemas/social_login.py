from pydantic import BaseModel, EmailStr, Field


class SocialLoginRequest(BaseModel):
    provider: str = Field(default="github", description="Social provider, e.g. github, facebook")
    provider_id: str = Field(min_length=1)
    email: EmailStr
    name: str | None = None

