from datetime import datetime, timedelta
from app.utils.date_utils import D

import bcrypt
import jwt
import re
from fastapi import APIRouter, Depends
from starlette.requests import Request

# TODO:
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.common.consts import JWT_SECRET, JWT_ALGORITHM
from app.database.conn import db
from app.database.models.members.index import Members
from app.database.models.email.index import EmailVerify
from app.models.member import MemberToken, MemberRegister, MemberLogin, MemberRegisterVerifyEmailSend, \
    MemberRegisterVerifyEmailCheck, MemberFindAccount, MemberFindAccountLook, MemberFindAccountChange
from app.service.email.send import email_verify_send, email_find_account_send
from app.utils.random import make_random, six_number_random
from app.success.index import Successful
from app.errors import exceptions as ex
from app.common.consts import ACCEPT_EMAIL_LIST, MAIN_DOMAIN
from app.redis.conn import redis_cache

"""
로그인/회원가입

"""

router = APIRouter(prefix="/auth")


@router.post("/register/verify/email/send", status_code=200)
async def register_verify_email_send(request: Request, reg_info: MemberRegisterVerifyEmailSend,
                                     background_tasks: BackgroundTasks, session: Session = Depends(db.session)):
    """
    `회원가입 - 이메일 검증 전송 API`\n
    :param background_tasks:
    :param request:
    :param reg_info:
    :param session:
    :return:
    """

    if not reg_info.email:
        return ex.CustomEx(msg="이메일이 입력되지 않았습니다.")
    if reg_info.email.split('@')[1] not in ACCEPT_EMAIL_LIST:
        return ex.CustomEx(msg="허용되지 않은 이메일입니다.")
    check_email_exist = await is_email_exist(session, reg_info.email)
    if check_email_exist:
        return ex.CustomEx(msg="이미 사용중인 이메일입니다.")

    # 10분 이내에 한 아이피당 10번 이상 요청 금지
    compare_datetime = D.datetime() - timedelta(minutes=10)
    count_email_verify = session.query(func.count(EmailVerify.id)).filter(
        (EmailVerify.ipaddress == request.state.ip) &
        (EmailVerify.created_time > compare_datetime) &
        (EmailVerify.type == "signup_email")
    ).scalar()

    if count_email_verify >= 10:
        return ex.CustomEx(msg="너무 많은 요청을 하셨습니다. 10분후에 재시도해주세요.")

    email_verify_secret_key = make_random(50)
    email_verify_code = six_number_random()
    EmailVerify.create(session, auto_commit=True, type="signup_email", email=reg_info.email, code=email_verify_code,
                       secret=email_verify_secret_key, ipaddress=request.state.ip)
    background_tasks.add_task(
        email_verify_send, reg_info.email, str(email_verify_code)
    )
    return Successful(dict(email_verify_secret_key=email_verify_secret_key))


@router.post("/register/verify/email/check", status_code=200)
async def register_verify_email_check(request: Request, reg_info: MemberRegisterVerifyEmailCheck,
                                      session: Session = Depends(db.session)):
    """
    `회원가입 - 이메일 검증 확인 API`\n
    :param request:
    :param reg_info:
    :param session:
    :return:
    """
    if not reg_info.email_verify_secret_key or not reg_info.code:
        return ex.CustomEx(msg="이메일 검증키와 인증코드가 전달되어야 합니다.")

    email_verify_check = EmailVerify.get(session, secret=reg_info.email_verify_secret_key, type="signup_email")

    if not email_verify_check:
        return ex.CustomEx(msg="검증키가 올바르지 않습니다. 새로고침하여 회원가입을 재시도하세요.")

    if email_verify_check.code != reg_info.code:
        return ex.CustomEx(msg="인증코드가 올바르지 않습니다.")

    if email_verify_check.status != 0:
        return ex.CustomEx(msg="이미 인증처리가 끝난 검증키입니다.")

    compare_datetime = D.datetime() - timedelta(hours=3)
    if email_verify_check.created_time < compare_datetime:
        return ex.CustomEx(msg="인증코드 유효기간이 지났습니다. 재인증 해주세요.")

    session.query(EmailVerify).filter(EmailVerify.id == email_verify_check.id).update({
        'status': 1
    })
    session.commit()

    return Successful(dict(msg='이메일 인증이 완료 되었습니다!'))


@router.post("/register", status_code=200)
async def register(request: Request, reg_info: MemberRegister, session: Session = Depends(db.session)):
    """
    `회원가입 API`\n
    :param reg_info:
    :param session:
    :return:
    """
    if not reg_info.member_id or not reg_info.email or not reg_info.password or not reg_info.nick:
        return ex.CustomEx(msg="전달되는 값에 빈칸이 있어서는 안됩니다.")
    if not reg_info.email_verify_secret_key:
        return ex.CustomEx(msg="이메일 인증이 완료되지 않았습니다.")

    if validate_member_id(reg_info.member_id):
        return ex.CustomEx(msg="아이디는 4글자 이상 16글자 이하 및 영어/숫자로만 이루어져야 합니다.")

    validated_password, validated_password_msg = validate_password(reg_info.password)
    if validated_password:
        return ex.CustomEx(msg=validated_password_msg)

    reg_info.nick = reg_info.nick.strip()
    reg_info.nick = re.sub(r"\s+", " ", reg_info.nick)
    validated_nick, validated_nick_msg = validate_nick(reg_info.nick)
    if validated_nick:
        return ex.CustomEx(msg=validated_nick_msg)

    check_member_id_exist = await is_member_id_exist(session, reg_info.member_id)
    if check_member_id_exist:
        return ex.CustomEx(msg="이미 사용중인 아이디입니다.")

    check_email_exist = await is_email_exist(session, reg_info.email)
    if check_email_exist:
        return ex.CustomEx(msg="이미 사용중인 이메일입니다.")

    check_nick_exist = await is_nick_exist(session, reg_info.nick)
    if check_nick_exist:
        return ex.CustomEx(msg="이미 사용중인 닉네임입니다.")

    check_email_verify_exist = EmailVerify.get(session, secret=reg_info.email_verify_secret_key, type="signup_email")
    if not check_email_verify_exist:
        return ex.CustomEx(msg="이메일 인증이 완료되지 않았습니다.")
    if check_email_verify_exist.email != reg_info.email:
        return ex.CustomEx(msg="회원가입 이메일과 인증된 이메일이 다릅니다.")
    if check_email_verify_exist.status != 1:
        return ex.CustomEx(msg="이메일 인증이 완료되지 않았습니다.")

    hash_pw = bcrypt.hashpw(reg_info.password.encode("utf-8"), bcrypt.gensalt())
    new_user = Members.create(session, auto_commit=True, member_id=reg_info.member_id, password=hash_pw,
                              email=reg_info.email, nick=reg_info.nick, secret=make_random(30), ipaddress=request.state.ip)
    token = dict(msg="성공적으로 회원가입 되었습니다! 환영합니다.",
                 expire_hours=6,
                 Authorization=f"Bearer {await create_access_token(member_id=reg_info.member_id,data=MemberToken.from_orm(new_user).dict(), expires_delta=6)}")
    return Successful(token)


@router.post("/login", status_code=200)
async def login(request: Request, user_info: MemberLogin, session: Session = Depends(db.session)):
    """
    `로그인 API`\n
    :param request:
    :param user_info:
    :param session:
    :return:
    """

    check_member_id_exist = Members.get(session, member_id=user_info.member_id)
    if not user_info.member_id or not user_info.password:
        return ex.CustomEx(msg="아이디 또는 비밀번호가 입력되지 않았습니다.")
    if not check_member_id_exist:
        return ex.CustomEx(msg="아이디 또는 비밀번호가 올바르지 않습니다")
    is_verified = bcrypt.checkpw(user_info.password.encode("utf-8"), check_member_id_exist.password.encode("utf-8"))
    if not is_verified:
        return ex.CustomEx(msg="아이디 또는 비밀번호가 올바르지 않습니다")

    session.query(Members).filter(Members.member_id == user_info.member_id).update({
        'last_log': D.datetime(),
        'ipaddress': request.state.ip
    })

    # Members.filter(session, member_id=user_info.member_id).update(auto_commit=True, last_log=D.datetime(),
    # ipaddress=request.state.ip)

    expire_hours = 6
    if user_info.auto_login:
        expire_hours = 24 * 15

    check_member_id_exist.ipaddress = request.state.ip

    token = dict(
        msg="로그인 완료",
        expire_hours=expire_hours,
        Authorization=f"Bearer {await create_access_token(member_id=user_info.member_id, data=MemberToken.from_orm(check_member_id_exist).dict(), expires_delta=expire_hours)}")

    session.commit()

    return Successful(token)


@router.post("/find/account", status_code=200)
async def find_account(request: Request, reg_info: MemberFindAccount,
                                     background_tasks: BackgroundTasks, session: Session = Depends(db.session)):
    """
    `계정 찾기 - 이메일로 비밀번호 재설정 링크 전송 API`\n
    :param background_tasks:
    :param request:
    :param reg_info:
    :param session:
    :return:
    """

    if not reg_info.email:
        return ex.CustomEx(msg="이메일이 입력되지 않았습니다.")
    if reg_info.email.split('@')[1] not in ACCEPT_EMAIL_LIST:
        return ex.CustomEx(msg="올바르지 않은 이메일입니다.")
    check_email_exist = await is_email_exist(session, reg_info.email)
    if not check_email_exist:
        return ex.CustomEx(msg="가입되지 않은 이메일입니다.")

    # 10분 이내에 한 아이피당 10번 이상 요청 금지
    compare_datetime = D.datetime() - timedelta(minutes=10)
    count_email_verify = session.query(func.count(EmailVerify.id)).filter(
        (EmailVerify.ipaddress == request.state.ip) &
        (EmailVerify.created_time > compare_datetime) &
        (EmailVerify.type == "find_account")
    ).scalar()

    if count_email_verify >= 6:
        return ex.CustomEx(msg="너무 많은 요청을 하셨습니다. 10분후에 재시도해주세요.")

    user = Members.get(session, email=reg_info.email)
    member_id = user.member_id

    secret_hash = make_random(50)
    EmailVerify.create(session, auto_commit=True, type="find_account", secret=secret_hash, email=reg_info.email, ipaddress=request.state.ip)
    background_tasks.add_task(
        email_find_account_send, reg_info.email, member_id, MAIN_DOMAIN + "/account/findpassword/?s=" + secret_hash
    )
    return Successful(dict(msg=" 이메일로 비밀번호를 변경하실 수 있는 링크를 발급 해드렸습니다! 지금 확인해주세요."))


@router.post("/find/account/look", status_code=200)
async def find_account_look(reg_info: MemberFindAccountLook, session: Session = Depends(db.session)):
    """
    `계정 찾기 - 해쉬값을 통해 유저정보 파악 API`\n
    :param request:
    :param reg_info:
    :param session:
    :return:
    """

    if not reg_info.hash_key:
        return ex.CustomEx(msg="해쉬값이 입력되지 않았습니다.")
    check_email_find = await verify_find_account(session, reg_info.hash_key)
    if not check_email_find:
        return ex.CustomEx(msg="만료된 해쉬값이거나 이미 비밀번호를 변경하셨습니다!")

    user = Members.get(session, email=check_email_find.email)

    return Successful(dict(member_id=user.member_id, email=user.email))


@router.post("/find/account/change", status_code=200)
async def find_account_change(request: Request, reg_info: MemberFindAccountChange, session: Session = Depends(db.session)):
    """
    `계정 찾기 - 비밀번호 변경 API`\n
    :param request:
    :param reg_info:
    :param session:
    :return:
    """

    if not reg_info.hash_key or not reg_info.password:
        return ex.CustomEx(msg="해쉬값 또는 비밀번호가 입력되지 않았습니다.")

    check_email_find = await verify_find_account(session, reg_info.hash_key)

    if not check_email_find:
        return ex.CustomEx(msg="만료된 해쉬값이거나 이미 비밀번호를 변경하셨습니다!")

    validated_password, validated_password_msg = validate_password(reg_info.password)
    if validated_password:
        return ex.CustomEx(msg=validated_password_msg)

    user = Members.get(session, email=check_email_find.email)
    await redis_cache.delete(user.member_id)
    hash_pw = bcrypt.hashpw(reg_info.password.encode("utf-8"), bcrypt.gensalt())

    session.query(Members).filter(Members.id == user.id).update({
        'password': hash_pw,
        'updated_password': D.datetime(),
        'ipaddress': request.state.ip
    })

    session.query(EmailVerify).filter(EmailVerify.id == check_email_find.id).update({
        'status': 1
    })

    session.commit()
    return Successful(dict(msg="비밀번호가 성공적으로 재설정 되었습니다. 로그인해주세요."))


async def is_member_id_exist(session, member_id: str):
    get_member_id = Members.get(session, member_id=member_id)
    if get_member_id:
        return True
    return False


async def is_email_exist(session, email: str):
    get_email = Members.get(session, email=email)
    if get_email:
        return True
    return False


async def is_nick_exist(session, nick: str):
    get_nick = Members.get(session, nick=nick)
    if get_nick:
        return True
    return False


async def verify_find_account(session, hash_key: str):
    get_verify = EmailVerify.get(session, type="find_account", secret=hash_key, status=0)
    compare_datetime = D.datetime() - timedelta(hours=3)
    if not get_verify:
        return False
    elif get_verify.created_time < compare_datetime:
        return False
    print('test')
    return get_verify


def validate_member_id(member_id):
    validate_condition = [
        lambda s: all(x.islower() or x.isdigit() for x in s),
        lambda s: any(x.islower() for x in s),
        lambda s: len(s) == len(s.replace(" ", "")),
        lambda s: len(s) >= 4,
        lambda s: len(s) <= 16,
    ]

    for validator in validate_condition:
        if not validator(member_id):
            return True


def validate_nick(nick):
    nick_temp = nick.replace(' ', '')
    if len(nick) < 2 or len(nick) > 12:
        return True, "닉네임은 2글자 이상 12글자 이하여야 합니다."
    elif not nick_temp.isalnum():
        return True, "닉네임은 한글/영어/숫자만 올 수 있습니다."

    return False, ""


def validate_password(password):
    if len(password) < 6 or len(password) > 20:
        return True, "비밀번호는 6글자 이상 20글자 이하여야 합니다."
    elif re.search('[0-9]+', password) is None:
        return True, "비밀번호는 최소 1개 이상의 숫자가 포함되어야 합니다."
    elif re.search('[a-zA-z]+', password) is None:
        return True, "비밀번호는 최소 1개 이상의 영어가 포함되어야 합니다."

    return False, ""


async def create_access_token(*, member_id: str = None, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Redis 등록
    await redis_cache.hset(member_id, encoded_jwt, 'login')
    await redis_cache.expire(member_id, expires_delta * 60 * 60)

    return encoded_jwt
