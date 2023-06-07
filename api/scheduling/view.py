import re
from typing import Dict, List, Literal, Optional

import aiohttp
import requests
from fastapi import APIRouter, Request, Body
from pydantic import BaseModel, conint

from api.scheduling.constans import *
from core.settings import ALGORITHM_SERVICE_URL
from db.models import TaskSet, Task, InterTaskContraints, SchedulingResult
from db.redis import redis_client
from utils.make_response import resp_200, resp_400, resp_404
from utils.result_schema import ResultListModel, ResultModel

base_router = APIRouter()


class TaskModel(BaseModel):
    """
    Pydantic task model used in post task set method
    """
    task_id: int
    cpu_dem: conint(ge=1)
    mem_dem: conint(ge=1)
    disk_dem: conint(ge=1)
    delay_constraint: Optional[int]
    image_tag: Optional[str] = "default"


class InterTaskConstraintsModel(BaseModel):
    a_task_id: int
    z_task_id: int
    bandwidth: Optional[int]
    delay: Optional[int]


class TaskSetModel(BaseModel):
    """
    Pydantic task set model used in post task set method
    """
    task_set_id: Optional[int]
    task_count: conint(ge=1)
    name: str
    tasks: List[TaskModel]
    inter_task_constraints: List[InterTaskConstraintsModel]
    start_flag: bool


class TaskSetResponseModel(BaseModel):
    """
    response model for get specific task set
    """
    task_set: TaskSet.get_pydantic()
    # tasks: List[Task.get_pydantic()]


class SchedulingResultResponseModel(BaseModel):
    """
    response model for get scheduling result
    """

    class TaskResult(BaseModel):
        task_id: int
        node_id: int

    task_set_id: int
    algorithm_type: str
    time_cost: float
    cost: int
    tail_latency: int
    avg_latency: int
    task_result_list: List[TaskResult]

@base_router.get("/task_sets", response_model=ResultListModel[List[TaskSet.get_pydantic()]],
                 summary="get task sets seperated by page")
async def list_task_sets(sort_by: Literal["ctime", "mtime"] = "ctime",
                         order_by: Literal["desc", "asc"] = "desc",
                         page: conint(ge=1) = 1,
                         page_size: conint(ge=1) = 20):
    """

    :param sort_by:
    :param order_by:
    :param page:
    :param page_size:
    :return:
    """
    task_set_query_set = TaskSet.objects
    count = await task_set_query_set.count()
    items = await task_set_query_set.order_by(getattr(getattr(TaskSet, sort_by), order_by)()).paginate(
        page=page, page_size=page_size).all()
    return resp_200(data={"count": count, "items": items})


@base_router.get("/task_set/{task_set_id}", response_model=ResultModel[TaskSetResponseModel],
                 summary="get specific task set and all tasks inside")
async def get_task_set(task_set_id: int):
    task_set = await TaskSet.objects.select_related(["all_tasks"]).get_or_none(
        id=task_set_id)
    if not task_set:
        return resp_404()
    return resp_200(data=task_set)


@base_router.post("/task_set", response_model=ResultModel[Dict], summary="create a scheduling task set")
async def post_task_set(request: Request, body: TaskSetModel):
    # count = await TaskSet.objects.filter(name=body.name).count()
    # if count > 0:
    #     return resp_400(msg="任务组标题已存在！")

    task_set = TaskSet(name=body.name, creator_id=0, task_count=body.task_count)
    if body.start_flag:
        task_set.state = 1
    else:
        task_set.state = 0

    await task_set.save()

    tasks: List[Task] = []
    for task in body.tasks:
        task_orm = Task(
            task_set_id=task_set.id,
            task_id=task.task_id,
            cpu_dem=task.cpu_dem,
            mem_dem=task.mem_dem,
            disk_dem=task.disk_dem,
            delay_constraint=task.delay_constraint,
            image_tag=task.image_tag,
            task_set=task_set
        )
        tasks.append(task_orm)

    await Task.objects.bulk_create(tasks)

    inter_task_constraints: List[InterTaskContraints] = []
    for itc in body.inter_task_constraints:
        itc_orm = InterTaskContraints(
            task_set_id=task_set.id,
            a_task_id=itc.a_task_id,
            z_task_id=itc.z_task_id,
            bandwidth=itc.bandwidth,
            delay=itc.delay,
            task_set=task_set
        )
        inter_task_constraints.append(itc_orm)

    if len(inter_task_constraints) > 0:
        await InterTaskContraints.objects.bulk_create(inter_task_constraints)

    await trigger_schedule_task(task_set.id, body)

    return resp_200(data={"id": task_set.id, "is_running": body.start_flag})


@base_router.put("/task_set", response_model=ResultModel[Dict], summary="update a scheduling task set")
async def put_task_set(request: Request, body: TaskSetModel = Body()):
    if not body.task_set_id:
        return resp_404()
    task_set = await TaskSet.objects.select_related(["all_tasks", "all_inter_task_constraints"]).get_or_none(
        id=body.task_set_id)
    if not task_set:
        return resp_404()
    if task_set.state == 2:
        return resp_404()

    # if task_set.name != body.name:
    #     count = await TaskSet.objects.filter(name=body.name).count()
    #     if count > 0:
    #         return resp_400()

    # if request.headers["user_id"] != task_set.creator_id:
    #     return resp_400()

    if task_set.state == 1:
        return resp_400()

    raw_tasks = {task.task_id: task for task in task_set.all_tasks}
    new_tasks = []
    update_tasks = []
    for task in body.tasks:
        if task.task_id in raw_tasks:
            raw_task = raw_tasks.pop(task.task_id)
            if task.cpu_dem != raw_task.cpu_dem or task.mem_dem != raw_task.mem_dem \
                    or task.disk_dem != raw_task.disk_dem or task.delay_constraint != raw_task.delay_constraint \
                    or task.image_tag != raw_task.image_tag:
                raw_task.cpu_dem = task.cpu_dem
                raw_task.mem_dem = task.mem_dem
                raw_task.disk_dem = task.disk_dem
                raw_task.delay_constraint = task.delay_constraint
                raw_task.image_tag = task.image_tag

                update_tasks.append(raw_task)
                continue

        new_task = Task(
            task_set_id=task_set.id,
            task_id=task.task_id,
            cpu_dem=task.cpu_dem,
            mem_dem=task.mem_dem,
            disk_dem=task.disk_dem,
            delay_constraint=task.delay_constraint,
            image_tag=task.image_tag,
            task_set=task_set
        )

        new_tasks.append(new_task)

    if new_tasks:
        await Task.objects.bulk_create(new_tasks)
    if update_tasks:
        await Task.objects.bulk_update(update_tasks)
    if raw_tasks:
        await Task.objects.filter(id__in=[task.id for task in raw_tasks.values()]).delete()

    raw_itcs = {(itc.a_task_id, itc.z_task_id): itc for itc in task_set.all_inter_task_constraints}
    new_itcs = []
    update_itcs = []
    for itc in body.inter_task_constraints:
        if (itc.a_task_id, itc.z_task_id) in raw_itcs:
            raw_itc = raw_itcs.pop((itc.a_task_id, itc.z_task_id))
            if itc.bandwidth != raw_itc.bandwidth or itc.delay != raw_itc.delay:
                raw_itc.delay = itc.delay
                raw_itc.bandwidth = itc.bandwidth

                update_itcs.append(raw_itc)
                continue

        new_itc = InterTaskContraints(
            task_set_id=task_set.id,
            a_task_id=itc.a_task_id,
            z_task_id=itc.z_task_id,
            bandwidth=itc.bandwidth,
            delay=itc.delay,
            task_set=task_set
        )

        new_itcs.append(new_itc)

    if new_itcs:
        await InterTaskContraints.objects.bulk_create(new_itcs)
    if update_itcs:
        await InterTaskContraints.objects.bulk_update(update_itcs)
    if raw_itcs:
        await InterTaskContraints.objects.filter(id__in=[itc.id for itc in raw_itcs.values()]).delete()

    if body.start_flag == 1:
        task_set.state = 1
        await task_set.save()
        await trigger_schedule_task(task_set.id, body)

    return resp_200(data={"id": task_set.id, "is_running": body.start_flag})


@base_router.get("/trigger/{task_set_id}")
async def trigger(task_set_id: int):
    await trigger_schedule_task(task_set_id)
    return resp_200(data="ok")


@base_router.get("/callback/{task_set_id}")
async def callback_func(task_set_id: int):
    count = await SchedulingResult.objects.filter(task_set_id=task_set_id).count()
    _algorithm_type = "default"
    task_set = await TaskSet.objects.select_related(["all_tasks"]).get_or_none(id=task_set_id)
    _result_list = [0 for i in range(len(task_set.all_tasks))]

    raw_result = await redis_client.hget(REDIS_KEY.format(task_set_id), REDIS_RESULT_FIELD)
    raw_result = str(raw_result, encoding='utf-8')
    raw_result_list = raw_result.splitlines()
    _tmp = raw_result_list[1].split()
    _cost, _tail_latency, _avg_latency = int(_tmp[0]), int(_tmp[1]), int(_tmp[2])
    if re.search(r"\d+.\d+", raw_result_list[0]):
        _time_cost = float(re.search(r"\d+.\d+", raw_result_list[0]).group())
    else:
        _time_cost = float(re.search(r"\d", raw_result_list[0]).group())

    if count == 0:
        scheduling_result = SchedulingResult(
            task_set_id=task_set_id,
            algorithm=_algorithm_type,
            time=_time_cost,
            cost=_cost,
            tail_latency=_tail_latency,
            avg_latency=_avg_latency
        )
        await scheduling_result.save()
    else:
        scheduling_result = await SchedulingResult.objects.get_or_none(task_set_id=task_set_id)
        scheduling_result.algorithm = _algorithm_type
        scheduling_result.time = _time_cost
        scheduling_result.cost = _cost
        scheduling_result.tail_latency = _tail_latency
        scheduling_result.avg_latency = _avg_latency
        await scheduling_result.update()

    for _result in raw_result_list[2:]:
        task_id = int(_result.split()[0])
        node_id = int(_result.split()[1])
        _result_list[task_id] = node_id

    for task in task_set.all_tasks:
        task.node_id = _result_list[task.task_id]

    await Task.objects.bulk_update(task_set.all_tasks)

    print(f"GET /api/scheduling/trigger/{task_set_id} HTTP/1.1 OK")

    return resp_200(data="ok")


@base_router.get("/result/{task_set_id}")
async def get_scheduling_result(task_set_id: int):
    count = await SchedulingResult.objects.filter(task_set_id=task_set_id).count()
    if count == 0:
        await trigger_schedule_task(task_set_id)
    result = await SchedulingResult.objects.get_or_none(task_set_id=task_set_id)
    task_set = await TaskSet.objects.select_related(["all_tasks"]).get_or_none(id=task_set_id)
    task_result_list: List[SchedulingResultResponseModel.TaskResult] = []
    for task in task_set.all_tasks:
        task_result_list.append(SchedulingResultResponseModel.TaskResult(task_id=task.task_id, node_id=task.node_id))

    scheduling_result = SchedulingResultResponseModel(
        task_set_id=task_set_id,
        algorithm_type=result.algorithm,
        time_cost=result.time,
        cost=result.cost,
        tail_latency=result.tail_latency,
        avg_latency=result.avg_latency,
        task_result_list=task_result_list
    )
    return resp_200(data=scheduling_result)


async def make_request(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            return await response.text()


async def trigger_schedule_task(id: int, task_set: Optional[TaskSetModel] = None):
    if not task_set:
        task_set = await TaskSet.objects.select_related(["all_tasks", "all_inter_task_constraints"]).get_or_none(id=id)
        task_count = [str(task_set.task_count)]
        itc_count = [str(len(task_set.all_inter_task_constraints))]
        tasks: List = []
        for task in task_set.all_tasks:
            task_list = [task.task_id, task.cpu_dem, task.mem_dem, task.disk_dem,
                         task.delay_constraint if task.delay_constraint else INT_MAX]
            tasks.append(" ".join([str(item) for item in task_list]))
        itcs: List = []
        for itc in task_set.all_inter_task_constraints:
            itc_list = [itc.a_task_id, itc.z_task_id, itc.bandwidth if itc.bandwidth else 0,
                        itc.delay if itc.delay else INT_MAX]
            itcs.append(" ".join([str(item) for item in itc_list]))
        task_set_input = "\n".join(task_count + tasks + itc_count + itcs)
        await redis_client.hset(REDIS_KEY.format(id), REDIS_INPUT_FIELD, task_set_input)
        requests.get(ALGORITHM_SERVICE_URL.format(id))
        await callback_func(id)
        return

    task_count = [str(len(task_set.tasks))]
    itc_count = [str(len(task_set.inter_task_constraints))]
    tasks: List = []
    for task in task_set.tasks:
        task_list = [task.task_id, task.cpu_dem, task.mem_dem, task.disk_dem,
                     task.delay_constraint if task.delay_constraint else INT_MAX]
        tasks.append(" ".join([str(item) for item in task_list]))
    itcs: List = []
    for itc in task_set.inter_task_constraints:
        itc_list = [itc.a_task_id, itc.z_task_id, itc.bandwidth if itc.bandwidth else 0,
                    itc.delay if itc.delay else INT_MAX]
        itcs.append(" ".join([str(item) for item in itc_list]))
    task_set_input = "\n".join(task_count + tasks + itc_count + itcs)
    await redis_client.hset(REDIS_KEY.format(id), REDIS_INPUT_FIELD, task_set_input)
    requests.get(ALGORITHM_SERVICE_URL.format(id))
    await callback_func(id)
