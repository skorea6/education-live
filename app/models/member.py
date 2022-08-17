from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr


class MemberLogin(BaseModel):
    member_id: str = None
    password: str = None
    auto_login: bool = False


class MemberRegister(BaseModel):
    member_id: str = None
    email: EmailStr = None
    password: str = None
    nick: str = None
    email_verify_secret_key: str = None


class MemberRegisterVerifyEmailSend(BaseModel):
    email: EmailStr = None


class MemberRegisterVerifyEmailCheck(BaseModel):
    email_verify_secret_key: str = None
    code: int = None


class MemberFindAccount(BaseModel):
    email: EmailStr = None


class MemberFindAccountLook(BaseModel):
    hash_key: str = None


class MemberFindAccountChange(BaseModel):
    password: str = None
    hash_key: str = None


class Token(BaseModel):
    Authorization: str = None


class MessageOk(BaseModel):
    message: str = Field(default="OK")


class MemberToken(BaseModel):
    id: int
    member_id: str = None
    email: str = None
    nick: str = None
    ranked: str = None
    per: int = None
    ipaddress: str = None
    exp: int = None
    secret: str = None

    class Config:
        orm_mode = True


class MemberMe(BaseModel):
    id: int
    member_id: str = None
    email: str = None
    nick: str = None
    ranked: str = None
    per: int = None
    ipaddress: str = None
    exp: int = None
    secret: str = None

    class Config:
        orm_mode = True


class MemberEdit(BaseModel):
    nick: str = None
    old_password: str = None
    new_password: str = None


class MemberDelete(BaseModel):
    password: str = None
    reason: str = None
