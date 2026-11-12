from pydantic import BaseModel

class FacebookLoginRequest(BaseModel):
    access_token: str

