import os
import pathlib

from PIL import Image


# 图片工具类
class ImageOperation:
    def __init__(self):
        print('init')

    @staticmethod
    def download(request, url, output_dir, rename):
        if url == '':
            print('url is empty, please input')
            pass

        if rename == '':
            rename = url.split('/')[-1]
            print(rename)

        output_path = os.path.join(output_dir, rename)
        request_img = request.do_request(url)
        with open(output_path, 'wb') as f:
            f.write(request_img.content)

    # 转为webp格式
    @staticmethod
    def convert_2_webp(output_dir, path, cover=False):
        if path == '':
            print('path is empty, please input path')
            pass
        if not os.path.isfile(path):
            print('image does not exist!')
            pass

        name = pathlib.Path(path).stem
        output_path = os.path.join(output_dir, f'{name}.webp')
        if os.path.isfile(output_path) and not cover:
            print(f'{output_path} already exist')
            pass

        # 尝试处理所有图片
        try:
            im = Image.open(path).convert("RGBA")
            im.save(output_path, "WEBP")
            return True
        # 输出处理失败的图片路径
        except:
            print(f'Error: {path} failed!')
            return False


if __name__ == '__main__':
    print('Test')
    input_dir_path = os.path.join(os.getcwd(), 'Icons')
    output_dir_path = os.path.join(os.getcwd(), 'WebpIcons')
    images = os.listdir(input_dir_path)[:6]
    # 处理所有图片
    for i in range(len(images)):
        image_path = os.path.join(input_dir_path, images[i])
        ImageOperation.convert_2_webp(output_dir_path, image_path)
