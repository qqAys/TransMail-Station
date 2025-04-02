from enum import Enum

from pydantic import BaseModel


class SystemRespondCode(int, Enum):
    """
    响应代码枚举类\n
    `200`: 响应成功
    """

    SUCCESS = 200


class SystemRespond(BaseModel):
    """
    系统类响应\n
    `code`: RespondCode 枚举类\n
    `message`: 返回数据
    """

    code: SystemRespondCode
    message: str
