import asyncio
from time import time

from fastapi import FastAPI

from .Database import cache_collection, image_collection


async def lifespan(app: FastAPI):
    timer_task = asyncio.create_task(timer())
    yield
    timer_task.cancel()


async def timer():
    while True:
        now_time = int(time())
        for cache_image in cache_collection.find():
            if (now_time - cache_image['time']) > 600:
                cache_collection.delete_one({'_id': cache_image['_id']})
        for head_image in image_collection.find():
            if (now_time - head_image['time']) > 1209600:
                image_collection.delete_one({'_id': head_image['_id']})
        await asyncio.sleep(600)
