from fastapi import Request, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.models import email_model, system_model
from app.services import database_service
from app.utils.util import Config, CustomException, logger

config = Config()
db_service = database_service.DatabaseService()

none_auth_resp = CustomException(401, "未授权的访问")
valid_api_keys = config.valid_api_keys

logger.debug(f"Valid api keys: {valid_api_keys}")


async def auth_dependencies(request: Request):
    method = request.method
    router_name = request.scope.get("route").name
    authorization = request.headers.get("authorization")

    logger.debug(f"{method} {router_name} {authorization}")

    if not authorization:
        logger.warning(f"no authorization")
        raise none_auth_resp

    try:
        scheme, api_key = authorization.split()
        if scheme.lower() != "bearer":
            raise none_auth_resp
    except ValueError:
        raise none_auth_resp

    if not api_key or api_key not in valid_api_keys:
        logger.warning(f"invalid api key: {api_key}")
        raise none_auth_resp


router = APIRouter()
dependencies = [
    Depends(auth_dependencies),
]

CANCEL = email_model.MailStatus.CANCEL.value


@router.get("/health", response_model=system_model.SystemRespond, tags=["system"])
def health():
    """
    健康检查
    """
    return JSONResponse(status_code=200, content={"code": 200, "message": "ok!"})


@router.post(
    "/email",
    response_model=email_model.EmailRespond,
    tags=["email"],
    dependencies=dependencies,
)
async def post_email(email: email_model.Email):
    """
    加入队列
    """
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
    "/email/{mailbox_id}",
    response_model=email_model.EmailRespond,
    tags=["email"],
    dependencies=dependencies,
)
async def get_email(mailbox_id: int):
    """
    获取详情
    """
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
    "/email/{mailbox_id}",
    response_model=email_model.EmailRespond,
    tags=["email"],
    dependencies=dependencies,
)
async def delete_email(mailbox_id: int):
    """
    取消发送
    """
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
