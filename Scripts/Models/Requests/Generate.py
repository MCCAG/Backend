from typing import Annotated, Optional, Literal
from pydantic import Base64Str, BaseModel, HttpUrl
from fastapi import Query

type Player = Annotated[str, Query(description='玩家的 ID')]
type Website = Annotated[HttpUrl, Query(description='皮肤站的网址')]
type SkinImage = Annotated[Base64Str, Query(description='上传的皮肤图像的 Base64 编码')]
type AvatarType = Annotated[Literal['big_head', 'full', 'head'], Query(description='生成头像类型')]


class GenerateImageRequest(BaseModel):
    skin_image: Base64Str
    avatar_type: Literal['big_head', 'full', 'head']


class GenerateAccountRequest(BaseModel):
    player: Player
    website: Optional[Website] = None
    avatar_type: Literal['big_head', 'full', 'head']
