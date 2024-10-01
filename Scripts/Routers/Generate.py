import binascii
from base64 import b64encode, b64decode
from io import BytesIO
from time import time
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from pydantic import Base64Str

from Scripts.Database import cache_collection
from Scripts.Network import fetch_skin
from Scripts.Renderer import render
from Scripts.Utils import generate_id

generate_router = APIRouter(prefix='/generate')

type SkinImage = Annotated[Base64Str, Query(description='上传的皮肤图像的 Base64 编码。')]
type AvatarType = Annotated[Literal['big_head', 'full', 'head'], Query(description='生成头像类型。')]


@generate_router.post('/file')
async def generate(skin_image: SkinImage, avatar_type: AvatarType) -> dict:
    """
    Generate an avatar head image from MoJaNg or skin website.
    Args:
        skin_image: the base64 code of skin's image file.
        avatar_type: generate type of head image.

    Returns:
        A base64 encoded head image data.
        Response: {'success': True, 'data': {'image': 'image_data'}}
    """
    try:
        skin_image = BytesIO(b64decode(skin_image))
    except binascii.Error:
        return {'success': False, 'message': '解码图片失败！'}

    avatar = render(skin_image, avatar_type)
    head_image = b64encode(avatar.getvalue()).decode()
    return {'success': True, 'data': {'image': head_image}}


@generate_router.post('/account')
async def generate(player: str, avatar_type: Literal['big_head', 'full', 'head'], website: str = None) -> dict:
    """
    Generate an avatar head image from 麻将 or skin website.
    Args:
        player: the skin's owner name.
        avatar_type: generate type of head image.
        website: the skin website url. If it's not provided, the skin will be fetched from Mojang.

    Returns:
        A base64 encoded head image data.
        Response: {'success': True, 'data': {'image': 'image data', 'id': 'this head image's id'}}

    """
    if not (avatar := await fetch_skin(player, website)):
        return {'success': False, 'message': '抓取皮肤失败！请稍后再试。'}

    image_id = generate_id(player, avatar_type, website if website else 'Mojang')
    if record := await cache_collection.find_one({'_id': image_id}, {'image': 1}):
        return {'success': True, 'data': record['image']}

    head_image = render(avatar, avatar_type)
    head_image = b64encode(head_image.getvalue()).decode()
    await cache_collection.insert_one({'_id': image_id, 'image': head_image, 'time': int(time())})
    return {'success': True, 'data': {'image': head_image, 'id': image_id}}
