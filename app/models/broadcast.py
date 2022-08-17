from pydantic.main import BaseModel


class BroadcastStart(BaseModel):
    title: str = None
    keyword: str = None
    detail: str = None
    password: str = None


class BroadcastList(BaseModel):
    member_id: str = None
    nick: str = None
    title: str = None
    keyword: str = None
    detail: str = None
    stream_code: str = None
    created_time: str = None

    class Config:
        orm_mode = True

