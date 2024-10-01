from typing import Annotated

from fastapi import APIRouter, Query

from Scripts.Database import image_collection, cache_collection

user_router = APIRouter(prefix='/user')

type ImageId = Annotated[str, Query(
    description='每个生成的头像都有一个编码，你可以使用这个编码来查询头像以及分享之类的操作（请注意，上传皮肤文件生成的无法分享）。')]
type UserId = Annotated[
    str, Query(description='用户 ID 对于每个设备来说是唯一的。可以采用 IP 地址、设备 ID 等，由前端生成。')]
type Background = Annotated[str, Query(description='背景图片的 css 样式，如 Url 或 Linear-gradient 等。')]


@user_router.post('/share')
async def share(image_id: ImageId, background: Background) -> dict:
    """
    分享一个头像。
    """
    if head_image := cache_collection.find_one({'_id': image_id}):
        data = {
            'background': background, 'likes': 0, 'users': '',
            '_id': image_id, 'time': head_image['time'],  'image': head_image['image']
        }
        image_collection.insert_one(data)
        return {'success': True}
    return {'success': False, 'message': '未找到头像！请尝试重新生成后再次分享。'}


@user_router.post('/like')
async def like(image_id: ImageId, user_id: UserId) -> dict:
    """
    点赞一个头像。
    """
    if head_image := image_collection.find_one({'_id': image_id}, {'likes': 1, 'users': 1}):
        if user_id in head_image['users']:
            return {'success': False, 'message': '你已经点过赞了！'}
        new_likes = (head_image['likes'] + 1)
        new_users = (head_image['users'] + '$' + user_id)
        image_collection.update_one({'_id': image_id}, {'$set': {'likes': new_likes, 'users': new_users}})
        return {'success': True}
    return {'success': False, 'message': '未找到头像！请确认分享是否过期。'}


@user_router.post('/unlike')
async def unlike(image_id: ImageId, user_id: UserId) -> dict:
    """
    取消点赞一个头像。
    """
    if head_image := image_collection.find_one({'_id': image_id}, {'likes': 1, 'users': 1}):
        if user_id not in head_image['users']:
            return {'success': False, 'message': '你还没点赞此头像！'}
        new_likes = (head_image['likes'] - 1)
        new_users = (head_image['users'].replace('$' + user_id, ''))
        image_collection.update_one({'_id': image_id}, {'$set': {'likes': new_likes, 'users': new_users}})
    return {'success': False, 'message': '未找到头像！请确认分享是否过期。'}
