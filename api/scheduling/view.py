from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Request, Body
from pydantic import BaseModel, conint

from db.models import TaskSet, Task
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
    image_tag: Optional[str]


class TaskSetModel(BaseModel):
    """
    Pydantic task set model used in post task set method
    """
    task_set_id: Optional[int]
    task_count: conint(ge=1)
    name: str
    tasks: List[TaskModel]
    start_flag: bool


class TaskSetResponseModel(BaseModel):
    """
    response model for get specific task set
    """
    task_set: TaskSet.get_pydantic()
    tasks: List[Task.get_pydantic()]


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
    task_set = await TaskSet.objects.get_or_none(id=task_set_id)
    if not task_set:
        return resp_404()
    tasks = await Task.objects.filter(task_set_id=task_set_id).all()
    return resp_200(data=TaskSetResponseModel(task_set=task_set, tasks=tasks))


@base_router.post("/task_set", response_model=ResultModel[Dict], summary="create a scheduling task set")
async def post_task_set(request: Request, body: TaskSetModel):
    count = await TaskSet.objects.filter(name=body.name).count()
    if count > 0:
        return resp_400(msg="任务组标题已存在！")

    task_set = TaskSet(name=body.name, creator_id=request.headers["user_id"], task_count=body.task_count)
    if body.start_flag:
        task_set.state = 1
    else:
        task_set.state = 0

    await task_set.save()

    tasks: List[Task] = []
    for task in body.tasks:
        task_orm = Task(
            task_set_id=task_set.id,
            cpu_dem=task.cpu_dem,
            mem_dem=task.mem_dem,
            disk_dem=task.disk_dem,
            delay_constraint=task.delay_constraint,
            image_tag=task.image_tag
        )
        tasks.append(task_orm)

    await Task.objects.bulk_create(tasks)

    return resp_200(data={"id": task_set.id, "is_running": body.start_flag})


@base_router.put("/task_set", response_model=ResultModel[Dict], summary="update a scheduling task set")
async def put_task_set(request: Request, body: TaskSetModel = Body()):
    if not body.task_set_id:
        return resp_404()
    task_set = await TaskSet.objects.select_related("all_tasks").get_or_none(id=body.task_set_id)
    if not task_set:
        return resp_404()
    if task_set.state == 2:
        return resp_404()

    if task_set.name != body.name:
        count = await TaskSet.objects.filter(name=body.name).count()
        if count > 0:
            return resp_400()

    if request.headers["user_id"] != task_set.creator_id:
        return resp_400()

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
            task_id=task.task_id,
            cpu_dem=task.cpu_dem,
            mem_dem=task.mem_dem,
            disk_dem=task.disk_dem,
            delay_constraint=task.delay_constraint,
            image_tag=task.image_tag
        )

        new_tasks.append(new_task)

    if new_tasks:
        await Task.objects.bulk_create(new_tasks)
    if update_tasks:
        await Task.objects.bulk_update(update_tasks)
    if raw_tasks:
        await Task.objects.filter(id__in=[task.id for task in raw_tasks.values()]).delete()

    if body.start_flag == 1:
        task_set.state = 1
        await task_set.save()

    return resp_200(data={"id": task_set.id, "is_running": body.start_flag})
