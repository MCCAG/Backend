from io import BytesIO
from pathlib import Path
from json import loads
from typing import Literal
from PIL import Image, ImageFilter, ImageOps

operation_path = Path('Data/Operations.json')
operation_data = loads(operation_path.read_text('Utf-8'))


def create_shadow(bordered_image: Image.Image, canvas: Image.Image, paste_position: tuple):
    """创建并粘贴阴影"""
    mask = bordered_image.split()[3]  # 仅获取透明度通道
    solid_image = Image.new('RGBA', bordered_image.size, (75, 85, 142, 255))
    shadow_image = Image.new('RGBA', bordered_image.size, (0, 0, 0, 0))
    shadow_image.paste(solid_image, (0, 0), mask)
    blurred_shadow = shadow_image.filter(ImageFilter.GaussianBlur(7))
    alpha = blurred_shadow.split()[3].point(lambda p: p * 0.6)
    blurred_shadow.putalpha(alpha)

    shadow_position = (paste_position[0] - 15, paste_position[1] - 10)
    base_image = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    base_image.paste(blurred_shadow, shadow_position, blurred_shadow)
    canvas.alpha_composite(base_image)


def process_image(resized_texture_image: Image.Image, crop_box: tuple, scale_factor: float, paste_position: tuple,
                  mirror: list, canvas: Image.Image):
    """处理图像的裁剪、缩放、阴影和粘贴"""
    cropped_image = resized_texture_image.crop(crop_box)
    if mirror:
        cropped_image = ImageOps.mirror(cropped_image)

    new_size = (
        int(cropped_image.size[0] * scale_factor),
        int(cropped_image.size[1] * scale_factor),
    )
    bordered_size = (new_size[0] + 30, new_size[1] + 30)
    bordered_image = Image.new('RGBA', bordered_size, (0, 0, 0, 0))
    bordered_image.paste(cropped_image.resize(new_size, Image.Resampling.NEAREST), (15, 15))

    # 创建阴影
    create_shadow(bordered_image, canvas, paste_position)

    # 粘贴实际图像
    adjusted_paste_position = (paste_position[0] - 15, paste_position[1] - 15)
    canvas.paste(bordered_image, adjusted_paste_position, bordered_image)


def get_operations(avatar_type: Literal['big_head', 'full', 'head'], skin_size: tuple):
    """确定操作列表根据头像类型和皮肤尺寸"""
    if avatar_type == 'head':
        return operation_data['head']
    if avatar_type == 'big_head':
        avatar_type = 'full'
    if skin_size == (64, 32):
        return operation_data[avatar_type]['1.7']
    return operation_data[avatar_type]['1.8']


def render(image: BytesIO, avatar_type: Literal['big_head', 'full', 'head']) -> BytesIO:
    """
    Args:
        image (BytesIO): 玩家皮肤材质文件，支持 `64x64` 和 `128x128`
        avatar_type (str): 头像类型，支持 'full' 和 'head' 以及 'big_head'
    """
    # 加载图像并创建画布
    player_texture = Image.open(image)
    canvas = Image.new('RGBA', (1000, 1000), (255, 255, 255, 0))

    skin_size = player_texture.size
    resized_texture_image = player_texture.resize(
        (128, 64) if skin_size == (64, 32) else (128, 128),
        Image.Resampling.NEAREST
    )

    operations = get_operations(avatar_type, skin_size)

    for crop_box, scale_factor, paste_position, *mirror in operations:
        process_image(resized_texture_image, crop_box, scale_factor, paste_position, mirror, canvas)

    if avatar_type == 'big_head':
        canvas = canvas.resize((1400, 1400), Image.Resampling.NEAREST)
        canvas = canvas.crop((200, 0, 1200, 1000))

    # 保存图像
    render_image = BytesIO()
    canvas.save(render_image, format='png')
    return render_image


if __name__ == '__main__':
    import asyncio
    from Scripts.Network import fetch_skin


    async def main():
        namelist = Path('Test/namelist.txt')
        for name in namelist.read_text('Utf-8').split('\n'):
            if not name:
                continue
            default_file_image = render(await fetch_skin('steve'), 'big_head')
            print(F'[{name}] 正在生成头像……')
            try:
                skin_image = await fetch_skin(name)
                file_image = render(skin_image, 'full')
            except AttributeError:
                file_image = default_file_image
                print(F'[{name}] 未找到的皮肤，使用默认头像。')
            with open(F'Test/{name}.png', 'wb') as file:
                file.write(file_image.getvalue())
            print(F'[{name}] 已生成头像，保存到文件夹中。')


    asyncio.run(main())
