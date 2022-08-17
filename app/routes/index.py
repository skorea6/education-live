import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.requests import Request
from inspect import currentframe as frame
from app.redis.conn import redis_cache

from sqlalchemy.orm import Session
from app.database.conn import db

router = APIRouter()


@router.get("/")
async def index(session: Session = Depends(db.session)):
    """
    ELB 상태 체크용 API
    :return:
    """

    # user = Users(status="active")
    # session.add(user)
    # session.commit()
    #
    # Users.create(session, auto_commit=True, name="코알라", status="deleted")
    # Users.create(session, auto_commit=True)

    # await redis_cache.set('test', '123')
    # test123 = await redis_cache.get('test')
    # await redis_cache.expire('test', 60)
    await redis_cache.hset('bro1', 'key1', '12345')
    await redis_cache.hset('bro1', 'key2', '54321')
    await redis_cache.expire('bro1', 10)
    # await asyncio.sleep(1)

    # await redis_cache.delete('bro1')
    key1 = await redis_cache.hget('bro1', 'key1')
    key2 = await redis_cache.hget('bro1', 'key2')

    print(key1)
    print(key2)

    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get("/test2")
async def test2():
    """
    ELB 상태 체크용 API
    :return:
    """

    key1 = await redis_cache.hget('bro1', 'key1')
    key2 = await redis_cache.hget('bro1', 'key2')

    print(key1)
    print(key2)

    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크용 API
    :return:
    """

    print("state.user", request.state.user)
    try:
        a = 1/0
    except Exception as e:
        request.state.inspect = frame()
        raise e
    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")
