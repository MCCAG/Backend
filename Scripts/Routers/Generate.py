import binascii
from base64 import b64encode, b64decode
from io import BytesIO
from time import time
from fastapi import APIRouter

from Scripts.Database import cache_collection
from Scripts.Network import fetch_skin
from Scripts.Renderer import render
from Scripts.Utils import generate_id
from Scripts.Models.Requests import GenerateAccountRequest, GenerateImageRequest

generate_router = APIRouter(prefix='/generate')


@generate_router.post('/file')
async def generate(request: GenerateImageRequest) -> dict:
    """
    Generate an avatar head image from MoJaNg or skin website.

    skin_image: the base64 code of skin's image file.
    avatar_type: generate type of head image.

    Returns:
        A base64 encoded head image data.
        Response: {'success': True, 'data': {'image': 'image_data'}}
    """
    try:
        skin_image = BytesIO(b64decode(request.skin_image))
    except binascii.Error:
        return {'success': False, 'message': '解码图片失败！'}

    avatar = render(skin_image, request.avatar_type)
    head_image = b64encode(avatar.getvalue()).decode()
    return {'success': True, 'data': {'image': head_image}}


@generate_router.post('/account')
async def generate(request: GenerateAccountRequest) -> dict:
    """
    Generate an avatar head image from 麻将 or skin website.

    player: the skin's owner name.
    avatar_type: generate type of head image.
    website: the skin website url. If it's not provided, the skin will be fetched from Mojang.

    Returns:
        A base64 encoded head image data.
        Response: {'success': True, 'data': {'image': 'image data', 'id': 'this head image's id'}}

    """
    if not (avatar := await fetch_skin(request.player, request.website)):
        return {'success': False, 'message': '抓取皮肤失败！请稍后再试。'}

    image_id = generate_id(request.player, request.avatar_type, request.website if request.website else 'Mojang')
    if record := cache_collection.find_one({'_id': image_id}, {'image': 1}):
        return {'success': True, 'data': {'image': record['image'], 'id': image_id}}

    head_image = render(avatar, request.avatar_type)
    head_image = b64encode(head_image.getvalue()).decode()
    cache_collection.insert_one({'_id': image_id, 'image': head_image, 'time': int(time())})
    return {'success': True, 'data': {'image': head_image, 'id': image_id}}
