from datetime import datetime
from enum import Enum
from typing import Union, List, Dict, Any

from pydantic import BaseModel, AnyHttpUrl

from app.utils.util import Config

# 邮件类型枚举动态模型，不同的类型会使用不同的发送地址
config = Config()
contact_lists = config.contact_lists
MailType = Enum('MailType', {key: key for key in contact_lists.keys()})


class MailStatus(str, Enum):
    """
    邮件状态枚举类\n
    `pending`: 待发送\n
    `sent`: 已发送\n
    `failed`: 发送失败\n
    `cancel`: 取消发送
    """
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCEL = "cancel"


class EmailRespondCode(int, Enum):
    """
    响应代码枚举类\n
    `200`: 加入发送队列成功\n
    `400`: 加入发送队列失败\n
    `401`: 未授权的访问\n
    `404`: 资源未找到
    """
    SUCCESS = 200
    FAILURE = 400
    NOT_FOUND = 404
    UNAUTHORIZED = 401


class Email(BaseModel):
    """
    邮件类\n
    `recipient`: 收件人，可传字符串 `xx_01@xxx.com,xx_02@xxx.com` 或可传列表 `["xx_01@xxx.com", "xx_02@xxx.com"]`\n
    `subject`: 邮件主题\n
    `body`: 邮件正文\n
    `type`: MailType 枚举类\n
    `scheduled_send_time`: 定时发送时间\n
    `callback_on_success`: 以 `http://` 或 `https://` 开头，邮件发送成功时回调，`3` 秒超时\n
    `callback_on_failure`: 以 `http://` 或 `https://` 开头，邮件发送失败时回调，`3` 秒超时\n
    `custom_data`: 以JSON格式传入其他数据，例如：`{"ad_id": 1090}`
    """
    recipient: Union[str, List[str]]
    subject: str
    body: str

    type: MailType
    scheduled_send_time: datetime | None = None

    callback_on_success: AnyHttpUrl | None = None
    callback_on_failure: AnyHttpUrl | None = None

    custom_data: Dict[str, Any] | None = None


class MailBoxRespond(BaseModel):
    mailbox_id: int
    message: str


class EmailRespond(BaseModel):
    """
    邮件类响应\n
    `code`: RespondCode 枚举类\n
    `data`: 返回数据
    """
    code: EmailRespondCode
    data: Union[str, Email, MailBoxRespond]


if __name__ == "__main__":
    pass
