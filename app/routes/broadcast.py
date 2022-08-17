from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from datetime import timedelta
from app.utils.date_utils import D
from app.database.conn import db

from app.success.index import Successful
from app.errors import exceptions as ex

from app.database.models.broadcast.index import LiveBroadcast
from app.database.models.members.index import Members
from app.models.broadcast import BroadcastStart, BroadcastList
from app.utils.random import make_random


router = APIRouter(prefix='/broadcast')


@router.get('/list')
async def broadcast_list(request: Request, session: Session = Depends(db.session)):
    result_query = session.query(
        LiveBroadcast.member_id,
        LiveBroadcast.title,
        LiveBroadcast.detail,
        LiveBroadcast.keyword,
        LiveBroadcast.stream_code,
        LiveBroadcast.created_time,
        Members.nick
    ).join(
        Members, LiveBroadcast.member_id == Members.member_id
    ).filter(LiveBroadcast.isdel == 0).order_by(LiveBroadcast.created_time.desc()).all()

    result = []

    for rq in result_query:
        result.append({
            'member_id': rq.member_id,
            'nick': rq.nick,
            'title': rq.title,
            'detail': rq.detail,
            'keyword': rq.keyword,
            'stream_code': rq.stream_code,
            'created_time': D.datetime_to_simple(rq.created_time)
        })

    return Successful(result)


@router.get('/detail/{stream_code}')
async def broadcast_list(request: Request, stream_code: str = None, session: Session = Depends(db.session)):
    if not stream_code:
        return ex.CustomEx(msg="stream_code 는 필수값입니다.")

    result_query = session.query(
        LiveBroadcast.id,
        LiveBroadcast.member_id,
        LiveBroadcast.title,
        LiveBroadcast.detail,
        LiveBroadcast.keyword,
        LiveBroadcast.stream_code,
        LiveBroadcast.created_time,
        Members.nick
    ).join(
        Members, LiveBroadcast.member_id == Members.member_id
    ).filter(
        (LiveBroadcast.isdel == 0) &
        (LiveBroadcast.stream_code == stream_code)
    ).first()

    if not result_query:
        return ex.CustomEx(msg="해당 stream_code 가 존재하지 않습니다.")

    return Successful({
            'room': result_query.id,
            'member_id': result_query.member_id,
            'nick': result_query.nick,
            'title': result_query.title,
            'detail': result_query.detail,
            'keyword': result_query.keyword,
            'stream_code': result_query.stream_code,
            'created_time': D.datetime_to_simple(result_query.created_time)
        })


@router.post('/start')
async def broadcast_start(request: Request, info_data: BroadcastStart, session: Session = Depends(db.session)):
    member = request.state.user
    if not member:
        return ex.CustomEx(msg="로그인 후 이용 가능한 서비스입니다.")

    if not info_data.title or not info_data.detail:
        return ex.CustomEx(msg="제목과 설명란은 필수로 입력해야 합니다.")

    stream_code = make_random(10)
    LiveBroadcast.create(session, auto_commit=True,
                         member_id=member.member_id,
                         title=info_data.title,
                         detail=info_data.detail,
                         keyword=info_data.keyword,
                         stream_code=stream_code
    )

    return Successful(dict(stream_code=stream_code, msg="이제 방송을 시작하세요! 방송 스트림키는 " + stream_code + " 입니다."))


@router.post('/stop')
async def broadcast_stop(request: Request, session: Session = Depends(db.session)):
    member = request.state.user
    if not member:
        return ex.CustomEx(msg="로그인 후 이용 가능한 서비스입니다.")

    session.query(LiveBroadcast).filter(LiveBroadcast.member_id == member.member_id).update({
        'isdel': 1
    })
    session.commit()

    return Successful(dict(msg="모든 방송이 중단 되었습니다!"))
