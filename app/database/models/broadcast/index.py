from sqlalchemy import Column, String, text, DateTime, CHAR, func
from sqlalchemy.dialects.mysql import INTEGER
from app.database.conn import Base
from app.database.schema import BaseMixin


class LiveBroadcast(Base, BaseMixin):
    __tablename__ = 'live_broadcast'

    id = Column(INTEGER(11), primary_key=True)
    member_id = Column(CHAR(25, 'utf8_bin'), nullable=False, index=True)
    title = Column(String(255, 'utf8_bin'), nullable=False)
    detail = Column(String(255, 'utf8_bin'))
    keyword = Column(String(255, 'utf8_bin'))
    stream_code = Column(String(255, 'utf8_bin'), nullable=False)
    isdel = Column(INTEGER(11), server_default=text("0"))
    created_time = Column(DateTime, nullable=False, default=func.now())
