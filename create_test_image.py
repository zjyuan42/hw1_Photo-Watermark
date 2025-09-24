import os
from PIL import Image, ImageDraw
import piexif
from datetime import datetime, timedelta

# 创建测试图片的函数
def create_test_image(output_path, date=None):
    # 创建一个简单的图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # 在图片上添加一些简单的内容
    draw.rectangle([(200, 150), (600, 450)], fill='white', outline='black', width=2)
    draw.ellipse([(300, 200), (500, 400)], fill='gray')
    
    # 设置EXIF日期信息
    if date is None:
        date = datetime.now() - timedelta(days=30)  # 使用30天前的日期
    
    date_str = date.strftime('%Y:%m:%d %H:%M:%S')
    
    # 创建EXIF数据
    exif_dict = {
        '0th': {},
        'Exif': {},
        'GPS': {},
        '1st': {},
        'thumbnail': None
    }
    
    # 添加日期信息到EXIF数据
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str.encode('utf-8')
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str.encode('utf-8')
    exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str.encode('utf-8')
    
    # 转换EXIF字典为字节数据
    exif_bytes = piexif.dump(exif_dict)
    
    # 保存图片，并包含EXIF数据
    image.save(output_path, exif=exif_bytes)
    print(f"已创建测试图片: {output_path}，拍摄日期: {date_str}")

# 创建测试目录
if not os.path.exists('test_images'):
    os.makedirs('test_images')

# 创建多个测试图片
dates = [
    datetime.now() - timedelta(days=30),
    datetime.now() - timedelta(days=15),
    datetime.now()
]

for i, date in enumerate(dates):
    output_path = os.path.join('test_images', f'test_image_{i+1}.jpg')
    create_test_image(output_path, date)

# 创建一个没有EXIF日期的测试图片
ooutput_path = os.path.join('test_images', 'test_image_no_exif.jpg')
# 创建图片但不添加EXIF信息
image = Image.new('RGB', (800, 600), color='lightgreen')
draw = ImageDraw.Draw(image)
draw.rectangle([(200, 150), (600, 450)], fill='white', outline='black', width=2)
image.save(output_path)
print(f"已创建无EXIF信息的测试图片: {output_path}")

print("所有测试图片创建完成!")
print("\n可以使用以下命令测试水印工具:")
print("python watermark.py test_images")
print("或测试单个图片:")
print("python watermark.py test_images\\test_image_1.jpg --font-size 36 --color 255,0,0 --position bottom_right")