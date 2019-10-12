import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from scrapyd_api import ScrapydAPI
import os
import shutil


def get_valid_img(request):
    # 获取随机颜色的函数
    def get_random_color():
        return random.randint(0, 100), random.randint(100, 170), random.randint(170, 255)
        # return 100, 200, 250

    # 生成一个图片对象
    img_obj = Image.new(
        'RGB',
        (110, 35),
        (232, 240, 254)
    )
    # 在生成的图片上写字符
    # 生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文件， 得到一个字体对象
    font_obj = ImageFont.truetype("./arial.ttf", 28)
    # 开始生成随机字符串并且写到图片上
    tmp_list = []
    for i in range(4):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw_obj.text((20 + 20 * i, 0), tmp, fill=get_random_color(), font=font_obj)

    # 保存到session
    request.session['checkcode'] = ''.join(tmp_list).upper()
    # 加干扰线
    width = 110  # 图片宽度（防止越界）
    height = 35
    for i in range(4):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw_obj.line((x1, y1, x2, y2), fill=get_random_color())

    # 加干扰点
    for i in range(40):
        draw_obj.point((random.randint(0, width), random.randint(0, height)), fill=get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw_obj.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())

    # 不需要在硬盘上保存文件，直接在内存中加载就可以
    io_obj = BytesIO()
    # 将生成的图片数据保存在io对象中
    img_obj.save(io_obj, "png")
    # 从io对象里面取上一步保存的数据
    data = io_obj.getvalue()

    return data


def uri(ip, port):
    return 'http://{ip}:{port}'.format(ip=ip, port=port)


def scrapyd_obj(url):
    try:
        return ScrapydAPI(url, timeout=10)
    except:
        return


def delete_file(file):
    path = os.path.splitext(file)[0]
    if os.path.exists(file):
        # 删除部署文件
        os.remove(file)
    if os.path.exists(path):
        # 删除部署目录
        shutil.rmtree(path)


def modify_file(src, content):
    # 修改文件
    old = open(src, 'r')
    lines = ''
    for line in old.readlines():
        if 'url =' in line:
            line = '%s\n' % content
        lines += line
    old.close()
    os.remove(src)
    new = open(src, 'w')
    print(lines, file=new)
    new.close()

def get_pages(total, per):
    # 分页计算器
    page = int(total / per)
    if total % per != 0:
        page += 1
    return page