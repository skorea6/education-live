from dataclasses import asdict
from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX
from app.database.conn import db, Base
from app.common.config import conf
from app.middlewares.token_validator import access_control
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth, member, broadcast
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.errors import exceptions as ex

# /docs 에 Authorize 버튼 만드는 방법
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def create_app():
    """
    앱 함수 실행
    :return:
    """
    c = conf()
    app = FastAPI(docs_url="/api/docs")  # docs_url=None, redoc_url=None, openapi_url=None
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)
    # 데이터 베이스 이니셜라이즈
    # Base.metadata.create_all(db.engine)
    # 레디스 이니셜라이즈

    # 미들웨어 정의
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 가장 먼저 실행되는 미들웨어 (아래부터 순차적으로 실행)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

    # 라우터 정의
    app.include_router(index.router, tags=["기본"])
    app.include_router(auth.router, tags=["계정"], prefix="/api")
    app.include_router(member.router, tags=["회원정보"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    app.include_router(broadcast.router, tags=["방송"], prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"status_code": 400, "msg": "전달된 형식이 잘못 되었습니다.", "error": str(exc)}
        )

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
