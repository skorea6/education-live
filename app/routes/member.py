from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from datetime import timedelta
from app.utils.date_utils import D
from app.database.conn import db

from app.database.models.members.index import Members, MembersDelete
from app.success.index import Successful
from app.errors import exceptions as ex

from app.models.member import MemberMe, MemberEdit, MemberDelete
from app.routes.auth import validate_password, validate_nick, is_nick_exist, create_access_token
from app.redis.conn import redis_cache

import bcrypt
import re

router = APIRouter(prefix='/member')


@router.get('/me')
async def member_me(request: Request):
    """
    `나의 정보 API`\n
    :param request:
    :return:
    """

    member = request.state.user
    # member_data = Members.get(id=member.id)
    change_to_list = MemberMe.from_orm(member)
    return Successful(dict(change_to_list))


@router.post('/edit')
async def member_edit(request: Request, member_info: MemberEdit, session: Session = Depends(db.session)):
    """
    `회원 정보 수정 API`\n
    :param session:
    :param member_info:
    :param request:
    :return:
    """

    member = request.state.user
    member_data = Members.get(session, id=member.id)

    if not member_info.old_password:
        return ex.CustomEx(msg="현재 비밀번호가 입력되지 않았습니다.")

    if member_info.nick:
        member_info.nick = member_info.nick.strip()
        member_info.nick = re.sub(r"\s+", " ", member_info.nick)
        validated_nick, validated_nick_msg = validate_nick(member_info.nick)
        if validated_nick:
            return ex.CustomEx(msg=validated_nick_msg)

    if (not member_info.nick and not member_info.new_password) or (
            member_info.nick == member_data.nick and not member_info.new_password):
        return ex.CustomEx(msg="새로운 닉네임 혹은 새로운 비밀번호를 입력해주세요.")

    is_verified = bcrypt.checkpw(member_info.old_password.encode("utf-8"), member_data.password.encode("utf-8"))
    if not is_verified:
        return ex.CustomEx(msg="현재 비밀번호가 올바르지 않습니다.")

    if member_info.new_password:
        validated_password, validated_password_msg = validate_password(member_info.new_password)
        if validated_password:
            return ex.CustomEx(msg=validated_password_msg)
        hash_pw = bcrypt.hashpw(member_info.new_password.encode("utf-8"), bcrypt.gensalt())

    if member_info.nick and member_info.nick != member_data.nick:
        check_nick_exist = await is_nick_exist(session, member_info.nick)
        if check_nick_exist:
            return ex.CustomEx(msg="이미 사용중인 닉네임입니다.")

        compare_datetime = D.datetime() - timedelta(hours=24)
        if member_data.updated_nick:
            if member_data.updated_nick > compare_datetime:
                return ex.CustomEx(msg="닉네임은 24시간에 한번만 바꿀 수 있습니다.")

    if member_info.new_password:
        await redis_cache.delete(member_data.member_id)
        session.query(Members).filter(Members.id == member_data.id).update({
            'password': hash_pw,
            'updated_password': D.datetime(),
            'ipaddress': request.state.ip
        })

    if member_info.nick and member_info.nick != member_data.nick:
        session.query(Members).filter(Members.id == member_data.id).update({
            'nick': member_info.nick,
            'updated_nick': D.datetime(),
            'ipaddress': request.state.ip
        })

    session.commit()
    return Successful(dict(msg="성공적으로 회원정보가 수정 되었습니다."))


@router.get('/login/extend')
async def member_extend_login(request: Request):
    """
    `로그인 기간 연장 API`\n
    :param request:
    :return:
    """
    member = request.state.user

    compare_datetime = D.timestamp_to_datetime(member.exp) - D.datetime()
    remain_minute = D.convert_seconds_to_kor_time(compare_datetime)

    if compare_datetime > timedelta(hours=2):
        return ex.CustomEx(msg="로그인 유지 시간이 2시간 이하일때 연장 가능합니다. (로그인 만료까지 " + remain_minute + " 남음)")

    await redis_cache.hdel(member.member_id, request.state.jwt_token)

    token = dict(msg="로그인 유지 시간이 최대로 연장 되었습니다.",
                 expire_hours=6,
                 Authorization=f"Bearer {await create_access_token(member_id=member.member_id, data=member.dict(), expires_delta=6)}")

    return Successful(token)


@router.get('/logout')
async def member_logout(request: Request):
    """
    `로그아웃 API`\n
    :param request:
    :return:
    """
    member = request.state.user
    await redis_cache.hdel(member.member_id, request.state.jwt_token)

    return Successful(dict(msg="로그아웃이 완료 되었습니다."))


@router.get('/logout/all')
async def member_logout(request: Request):
    """
    `로그아웃 (모든 기기에서) API`\n
    :param request:
    :return:
    """
    member = request.state.user
    await redis_cache.delete(member.member_id)

    return Successful(dict(msg="모든 기기에서 로그아웃이 완료 되었습니다."))


@router.post('/delete')
async def member_delete(request: Request, member_info: MemberDelete, session: Session = Depends(db.session)):
    """
    `회원 탈퇴 API`\n
    :param session:
    :param member_info:
    :param request:
    :return:
    """

    member = request.state.user
    member_data = Members.get(session, id=member.id)

    if not member_info.password:
        return ex.CustomEx(msg="현재 비밀번호가 입력되지 않았습니다.")

    is_verified = bcrypt.checkpw(member_info.password.encode("utf-8"), member_data.password.encode("utf-8"))
    if not is_verified:
        return ex.CustomEx(msg="현재 비밀번호가 올바르지 않습니다.")

    MembersDelete.create(session, member_id=member_data.member_id, email=member_data.email, nick=member_data.nick,
                         ranked=member_data.ranked, secret=member_data.secret, reason=member_info.reason,
                         ipaddress=request.state.ip)
    session.query(Members).filter(Members.id == member_data.id).delete()

    session.commit()
    await redis_cache.delete(member_data.member_id)

    return Successful(dict(msg="성공적으로 회원탈퇴 되었습니다. 이용해주셔서 감사합니다."))
