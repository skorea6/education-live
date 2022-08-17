from sqlalchemy import CHAR, Column, DateTime, String, Text, text, func
from sqlalchemy.dialects.mysql import INTEGER
from app.database.conn import Base
from app.database.schema import BaseMixin


class Members(Base, BaseMixin):
    __tablename__ = 'members'

    id = Column(INTEGER(11), primary_key=True)
    member_id = Column(CHAR(25, 'utf8_bin'), nullable=False, index=True)
    email = Column(String(255, 'utf8_bin'), nullable=False)
    nick = Column(CHAR(25, 'utf8_bin'), nullable=False)
    ranked = Column(CHAR(25, 'utf8_bin'), server_default=text("'bronze'"))
    status = Column(INTEGER(11), server_default=text("0"))
    per = Column(INTEGER(11), server_default=text("0"))
    secret = Column(String(255, 'utf8_bin'), nullable=False)
    password = Column(Text(collation='utf8_bin'), nullable=False)
    last_log = Column(DateTime)
    updated_nick = Column(DateTime)
    updated_password = Column(DateTime)
    created_time = Column(DateTime, nullable=False, default=func.now())
    ipaddress = Column(String(255, 'utf8_bin'))


class MembersDelete(Base, BaseMixin):
    __tablename__ = 'members_delete'

    id = Column(INTEGER(11), primary_key=True)
    member_id = Column(CHAR(25, 'utf8_bin'), nullable=False)
    email = Column(String(255, 'utf8_bin'), nullable=False)
    nick = Column(CHAR(25, 'utf8_bin'), nullable=False)
    ranked = Column(CHAR(25, 'utf8_bin'))
    secret = Column(String(255, 'utf8_bin'))
    reason = Column(Text(collation='utf8_bin'))
    created_time = Column(DateTime, nullable=False, default=func.now())
    ipaddress = Column(String(255, 'utf8_bin'))
