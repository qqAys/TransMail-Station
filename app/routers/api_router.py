from fastapi import Header, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models import email_model, system_model
from app.services.database_service import db_service
from app.utils.util import Config

none_auth_resp = JSONResponse(
    status_code=401, content={"code": 401, "data": "未授权的访问"}
)

router = APIRouter()

CANCEL = email_model.MailStatus.CANCEL.value


@router.get("/health", response_model=system_model.SystemRespond, tags=["system"])
def health():
    """
    健康检查
    """
    return JSONResponse(status_code=200, content={"code": 200, "message": "ok!"})


@router.post("/email", response_model=email_model.EmailRespond, tags=["email"])
async def post_email_route(email: email_model.Email, authorization: str = Header(None)):
    """
    加入队列
    """
    config = Config()
    valid_api_keys = config.valid_api_keys

    if not authorization:
        return none_auth_resp

    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            return none_auth_resp
    except ValueError:
        return none_auth_resp

    if not api_key or api_key not in valid_api_keys:
        return none_auth_resp

    mailbox_id = db_service.put_record(email)

    if mailbox_id is not None:
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "data": {"mailbox_id": mailbox_id, "message": "邮件已加入队列"},
            },
        )
    else:
        return JSONResponse(
            status_code=400, content={"code": 400, "data": "邮件加入队列失败"}
        )


@router.get(
    "/email/{mailbox_id}", response_model=email_model.EmailRespond, tags=["email"]
)
async def get_email_route(mailbox_id: int, authorization: str = Header(None)):
    """
    获取详情
    """
    config = Config()
    valid_api_keys = config.valid_api_keys

    if not authorization:
        return none_auth_resp

    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            return none_auth_resp
    except ValueError:
        return none_auth_resp

    if not api_key or api_key not in valid_api_keys:
        return none_auth_resp

    record = db_service.get_record(mailbox_id)

    if len(record) == 0:
        return JSONResponse(
            status_code=404, content={"code": 404, "data": "邮件不存在"}
        )
    else:
        return JSONResponse(
            status_code=200, content={"code": 200, "data": jsonable_encoder(record)}
        )


@router.delete(
    "/email/{mailbox_id}", response_model=email_model.EmailRespond, tags=["email"]
)
async def delete_email_route(mailbox_id: int, authorization: str = Header(None)):
    """
    取消发送
    """
    config = Config()
    valid_api_keys = config.valid_api_keys

    if not authorization:
        return none_auth_resp

    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            return none_auth_resp
    except ValueError:
        return none_auth_resp

    if not api_key or api_key not in valid_api_keys:
        return none_auth_resp

    row_count = db_service.update_record(mailbox_id, CANCEL)

    if row_count == 1:
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "data": {"mailbox_id": mailbox_id, "message": "计划发送已取消"},
            },
        )
    else:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "data": "计划发送取消失败，邮件可能已发送"},
        )
