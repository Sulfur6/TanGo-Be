from datetime import datetime
from typing import Optional

import ormar
from sqlalchemy import func

from db.database import BaseMeta


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'user'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=128)
    password: str = ormar.String(max_length=128)


class NetworkNode(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'network_node'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=32)
    cpu: int = ormar.Integer()
    mem: int = ormar.Integer()
    disk: int = ormar.Integer()
    cpu_rem: int = ormar.Integer()
    mem_rem: int = ormar.Integer()
    disk_rem: int = ormar.Integer()
    unit_cpu_price: int = ormar.Integer()
    unit_mem_price: int = ormar.Integer()
    unit_disk_price: int = ormar.Integer()


class NetworkNodeDelay(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'network_node_delay'

    id: int = ormar.Integer(primary_key=True)
    node_id: int = ormar.Integer()
    geo_place_id: int = ormar.Integer()
    delay: int = ormar.Integer()


class TaskSet(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'task_set'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=128)
    task_count: int = ormar.Integer()
    state: int = ormar.SmallInteger(default=0)
    creator_id: int = ormar.Integer()
    ctime: datetime = ormar.DateTime(server_default=func.now(), timezone=True)
    mtime: datetime = ormar.DateTime(
        server_default=func.now(),
        default=datetime.now, timezone=True)


class Task(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'task'

    id: int = ormar.Integer(primary_key=True)
    task_id: int = ormar.Integer()
    task_set_id: int = ormar.Integer()
    node_id: Optional[int] = ormar.Integer(nullable=True)
    cpu_dem: int = ormar.Integer()
    mem_dem: int = ormar.Integer()
    disk_dem: int = ormar.Integer()
    delay_constraint: int = ormar.Integer()
    image_tag: Optional[str] = ormar.String(max_length=32, nullable=True)
    task_set: TaskSet = ormar.ForeignKey(
        TaskSet, name="task_set_id", related_name="all_tasks"
    )


class InterTaskContraints(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'inter_task_constraints'

    id: int = ormar.Integer(primary_key=True)
    task_set_id: int = ormar.Integer()
    a_task_id: int = ormar.Integer()
    z_task_id: int = ormar.Integer()
    bandwidth: int = ormar.Integer()
    delay: int = ormar.Integer()
    task_set: TaskSet = ormar.ForeignKey(
        TaskSet, name="task_set_id", related_name="all_inter_task_constraints"
    )


class InterNetworkNode(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'inter_network_node'

    id: int = ormar.Integer(primary_key=True)
    a_node_id: int = ormar.Integer()
    z_node_id: int = ormar.Integer()
    bandwidth: int = ormar.Integer()
    delay: int = ormar.Integer()


class SchedulingResult(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'scheduling_result'

    id: int = ormar.Integer(primary_key=True)
    task_set_id: int = ormar.Integer()
    algorithm: str = ormar.String(max_length=256)
    time: float = ormar.Float()
    cost: int = ormar.BigInteger()
    tail_latency: int = ormar.Integer()
    avg_latency: int = ormar.Integer()
