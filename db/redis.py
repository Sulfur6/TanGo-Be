import json
from typing import Union

from aioredis import Redis

from core import settings


class RedisPlus(Redis):
    """ 继承 Redis, 并添加自己的方法 """

    def __init__(self, redis_psm=None, skip_service_discovery=False, disable_auth=False,
                 **kwargs):
        super().__init__(**kwargs)

        from_url = False

        if kwargs.get("connection_pool"):
            from_url = True

        # trick
        if not from_url:
            self.connection_pool.connection_kwargs.update({
                "redis_psm": redis_psm,
                "skip_service_discovery": skip_service_discovery,
                "disable_auth": disable_auth,
            })

    async def list_loads(self, key: str, num: int = -1) -> list:
        """
        将列表字符串转为对象

        :param key: 列表的key
        :param num: 最大长度(默认值 0-全部)
        :return: 列表对象
        """
        todo_list = await self.lrange(key, 0, (num - 1) if num > -1 else num)
        return [json.loads(todo) for todo in todo_list]

    async def cus_lpush(self, key: str, value: Union[str, list, dict]):
        """
        向列表右侧插入数据

        :param key: 列表的key
        :param value: 插入的值
        """
        text = json.dumps(value)
        await self.lpush(key, text)

    async def get_list_by_index(self, key: str, idx: int) -> object:
        """
        根据索引得到列表值

        :param key: 列表的值
        :param idx: 索引值
        :return:
        """
        value = await self.lindex(key, idx)
        return json.loads(value)


redis_client = RedisPlus.from_url(settings.REDIS_URL)


async def init_redis_pool() -> RedisPlus:
    return redis_client
