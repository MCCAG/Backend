from io import BytesIO
from typing import Optional
from pydantic import HttpUrl

from httpx import AsyncClient

client = AsyncClient()


async def request(url: str) -> Optional[dict]:
    response = await client.get(url)
    if response.status_code == 200:
        return response.json()


async def download(url: HttpUrl) -> Optional[BytesIO]:
    file_bytes = BytesIO()
    async with client.stream('GET', url) as stream:
        if stream.status_code != 200:
            return
        async for chunk in stream.aiter_bytes():
            file_bytes.write(chunk)
    file_bytes.seek(0)
    return file_bytes


async def fetch_skin(player: str, website: HttpUrl = None) -> Optional[BytesIO]:
    if website is None:
        if data := await request(F'https://api.mojang.com/users/profiles/minecraft/{player}'):
            if uuid := data.get('id'):
                return await download(F'https://crafatar.com/skins/{uuid}')
        return None
    website = str(website)
    website = website.rstrip('/')
    if data := await request(F'{website}/csl/{player}.json'):
        if skin_data := data.get('skins'):
            skin_data = tuple(skin_data.values())
            return await download(F'{website}/textures/{skin_data[0]}')


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(fetch_skin('NKeishi', 'https://littleskin.cn/')))
