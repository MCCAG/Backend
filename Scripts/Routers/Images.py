from random import choices

from typing import Annotated
from fastapi import APIRouter, Query

from Scripts.Database import image_collection

image_router = APIRouter(prefix='/images')

type ImageId = Annotated[str, Query(
    description='每个生成的头像都有一个编码，你可以使用这个编码来查询头像以及分享之类的操作（请注意，上传皮肤文件生成的无法分享）。')]


@image_router.get('/query')
async def query(image_id: ImageId) -> dict:
    """
    通过头像 id 获取头像。
    """
    if head_image := image_collection.find_one({'_id': image_id}, {'background': 1, 'image': 1}):
        return {'success': True, 'data': dict(head_image)}
    return {'success': False, 'message': '未找到头像！请确认头像 ID 是否正确。'}


@image_router.get('/newest')
async def newest() -> dict:
    """
    获取最新头像。
    """
    images = image_collection.find(sort=[('time', -1)], limit=30)
    return {'success': True, 'data': tuple(images)}


@image_router.get('/hottest')
async def hottest() -> dict:
    """
    获取最热头像。
    """
    images = image_collection.find(sort=[('likes', -1)], limit=6)
    return {'success': True, 'data': choices(tuple(images), k=6)}
