"""define all response_model here"""
from typing import TypeVar, Generic, Optional, Union, Any

from pydantic import BaseModel
from pydantic.generics import GenericModel

SchemasType = TypeVar("SchemasType", bound=BaseModel)


class ResultModel(GenericModel, Generic[SchemasType]):
    """ 普通结果验证 """
    code: int
    data: Union[SchemasType, Any]
    msg: Optional[str]


class ResultList(GenericModel, Generic[SchemasType]):
    """
    定义分页获取数据的 model
    data_list: 当前页的数据
    count: 总数量，并非 len(data_list)
    """
    items: Union[SchemasType, Any]
    count: int


class ResultListModel(GenericModel, Generic[SchemasType]):
    """ 列表结果验证 """
    code: int
    data: ResultList
    msg: Optional[str]
