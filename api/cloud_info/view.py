from typing import List, Literal

from fastapi import APIRouter, Path, Request
from pydantic import BaseModel, conint

from db.models import NetworkNode, NetworkNodeDelay, InterNetworkNode
from db.redis import redis_client
from utils.make_response import resp_200, resp_404
from utils.result_schema import ResultListModel, ResultModel

base_router = APIRouter()


class NetworkNodeResponse(NetworkNode.get_pydantic()):
    class Delay(BaseModel):
        geo_place_id: int
        delay: int

    delay: List[Delay]


@base_router.get("/nodes", response_model=ResultListModel[List[NetworkNode.get_pydantic()]],
                 summary="get network nodes split by page")
async def list_network_nodes(sort_by: Literal["id"] = "id",
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
    network_nodes_query_set = NetworkNode.objects
    count = await network_nodes_query_set.count()
    items = await network_nodes_query_set.order_by(getattr(getattr(NetworkNode, sort_by), order_by)()).paginate(
        page=page, page_size=page_size).all()
    return resp_200(data={"count": count, "items": items})


@base_router.get("/node/{node_id}", response_model=ResultModel[NetworkNodeResponse],
                 summary="get information of specific network node")
async def get_network_node(request: Request, node_id: int = Path(description="network node id")):
    """

    :param request:
    :param node_id:
    :return:
    """
    network_node = await NetworkNode.objects.get_or_none(id=node_id)
    if not network_node:
        return resp_404(data="no such record")

    network_node_delay = await NetworkNodeDelay.objects.filter(node_id=network_node.id).all()
    detail = network_node.dict()
    network_node_delay = [{"geo_place_id": delay.geo_place_id, "delay": delay.delay} for delay in network_node_delay]
    detail["delay"] = network_node_delay
    return resp_200(data=detail)


@base_router.get("/sync_cloud_info")
async def sync_cloud_info():
    network_nodes = await NetworkNode.objects.all()
    inter_network_nodes = await InterNetworkNode.objects.all()
    network_node_count = [str(len(network_nodes))]
    inn_count = [str(len(inter_network_nodes))]
    network_node_lines: List = []
    inn_lines: List = []
    for node in network_nodes:
        network_node_delay = await NetworkNodeDelay.objects.filter(node_id=node.id).all()
        tail_delay = -1
        avg_delay = 0
        for delay in network_node_delay:
            tail_delay = max(tail_delay, delay.delay)
            avg_delay += delay.delay
        avg_delay //= len(network_node_delay)
        node_list = [node.id, node.cpu, node.mem, node.disk, node.cpu_rem, node.mem_rem, node.disk_rem,
                     node.unit_cpu_price, node.unit_mem_price, node.unit_disk_price, tail_delay, avg_delay]
        network_node_lines.append(" ".join([str(item) for item in node_list]))
    for inn in inter_network_nodes:
        inn_list = [inn.a_node_id, inn.z_node_id, inn.bandwidth, inn.delay]
        inn_lines.append(" ".join([str(item) for item in inn_list]))
    network_node_input = "\n".join(network_node_count + network_node_lines + inn_count + inn_lines)
    await redis_client.set("cloud_info", network_node_input)
