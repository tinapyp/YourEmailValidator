from pydantic import BaseModel


class EmailResponse(BaseModel):
    email: str
    is_valid: bool
    message: str = None


class SingleEmailRequest(BaseModel):
    email: str


class BulkEmailRequest(BaseModel):
    email: list[str]
