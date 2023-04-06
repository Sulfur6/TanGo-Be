from typing import Union, Type, Any

from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.responses import Response

from utils.result_schema import SchemasType


# 因为 data 数据要符合 SchemasType 模型，不符合 JSONResponse 的序列化
def resp_200(code: int = 0, data: Union[Type[SchemasType], Any] = None,
             msg: str = "Success"):
    return {"code": code, "data": data, "msg": msg}


def resp_400(code: int = 0, data: str = None,
             msg: str = "Bad Request") -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": code, "msg": msg, "data": data})


def resp_401(code: int = 0, data: str = "Unauthorized",
             msg: str = "Unauthorized") -> Response:
    return ORJSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                          content={"code": code, "msg": msg, "data": data})


def resp_403(code: int = 0, data: str = None,
             msg: str = "Request Forbidden") -> Response:
    return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                          content={"code": code, "msg": msg, "data": data})


def resp_404(code: int = 0, data: str = None,
             msg: str = "Not Found") -> Response:
    return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                          content={"code": code, "msg": msg, "data": data})


def resp_406(code: int = 0, data: str = None,
             msg: str = "Not Acceptable") -> Response:
    return ORJSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                          content={"code": code, "msg": msg, "data": data})


def resp_408(code: int = 0, data: str = None,
             msg: str = "Request Timeout") -> Response:
    return ORJSONResponse(status_code=status.HTTP_408_REQUEST_TIMEOUT,
                          content={"code": code, "msg": msg, "data": data})


def resp_410(code: int = 0, data: str = None,
             msg: str = "URI No Longer Exists") -> Response:
    return ORJSONResponse(status_code=status.HTTP_410_GONE,
                          content={"code": code, "msg": msg, "data": data})


def resp_500(code: int = 0, data: str = None,
             msg: Union[list, dict, str] = "Internal Server Error"
             ) -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": code, "msg": msg, "data": data})


def resp_501(code: int = 0, data: str = None,
             msg: str = "Not Implemented") -> Response:
    return ORJSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED,
                          content={"code": code, "msg": msg, "data": data})


def resp_502(code: int = 0, data: str = None,
             msg: str = "Bad Gateway") -> Response:
    return ORJSONResponse(status_code=status.HTTP_502_BAD_GATEWAY,
                          content={"code": code, "msg": msg, "data": data})


def resp_503(code: int = 0, data: str = None,
             msg: str = "Service Unavailable") -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"code": code, "msg": msg, "data": data})


def resp_504(code: int = 0, data: str = None,
             msg: str = "Gateway Timeout") -> Response:
    return ORJSONResponse(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                          content={"code": code, "msg": msg, "data": data})


def resp_505(code: int = 0, data: str = None,
             msg: str = "HTTP Version Not Supported") -> Response:
    return ORJSONResponse(
        status_code=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED,
        content={"code": code, "msg": msg, "data": data})
