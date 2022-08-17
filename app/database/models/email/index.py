from sqlalchemy import CHAR, Column, DateTime, String, text, func
from sqlalchemy.dialects.mysql import INTEGER
from app.database.conn import Base
from app.database.schema import BaseMixin


class EmailVerify(Base, BaseMixin):
    __tablename__ = 'email_verify'

    id = Column(INTEGER(11), primary_key=True)
    type = Column(CHAR(25, 'utf8_bin'))
    email = Column(String(255, 'utf8_bin'), nullable=False)
    code = Column(INTEGER(11))
    secret = Column(String(255, 'utf8_bin'), nullable=False)
    status = Column(INTEGER(11), server_default=text("0"))
    ipaddress = Column(String(255, 'utf8_bin'))
    created_time = Column(DateTime, nullable=False, default=func.now())
