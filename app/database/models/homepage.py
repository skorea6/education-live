from sqlalchemy import Column, String, Table
from app.database.conn import Base


metadata = Base.metadata

t_homepage = Table(
    'homepage', metadata,
    Column('page_title', String(255, 'utf8_bin')),
    Column('page_des', String(255, 'utf8_bin')),
    Column('page_keyword', String(255, 'utf8_bin')),
    Column('page_domain', String(255, 'utf8_bin')),
    Column('img_cdn_domain', String(255, 'utf8_bin')),
    Column('vod_cdn_domain', String(255, 'utf8_bin')),
    Column('live_cdn_domain', String(255, 'utf8_bin')),
    Column('iframe_domain', String(255, 'utf8_bin')),
    Column('chat_domain', String(255, 'utf8_bin')),
    Column('api_domain', String(255, 'utf8_bin'))
)