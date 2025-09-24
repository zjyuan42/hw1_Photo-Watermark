import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import piexif
from datetime import datetime

class ImageWatermark:
    def __init__(self, image_path, font_size=24, font_color=(255, 255, 255), position='bottom_right'):
        self.image_path = image_path
        self.font_size = font_size
        self.font_color = font_color
        self.position = position
        self.output_dir = self._create_output_dir()
        
    def _create_output_dir(self):
        """创建输出目录"""
        base_dir = os.path.dirname(self.image_path)
        if not base_dir:
            base_dir = '.'
        output_dir = os.path.join(base_dir, os.path.basename(base_dir) + '_watermark')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    
    def _get_exif_date(self, image_path):
        """从图片的EXIF信息中获取拍摄日期"""
        try:
            image = Image.open(image_path)
            exif_data = piexif.load(image.info.get('exif', b''))
            
            # 尝试从不同的EXIF标签中获取日期
            date_tags = [
                exif_data.get('Exif', {}).get(piexif.ExifIFD.DateTimeOriginal),
                exif_data.get('Exif', {}).get(piexif.ExifIFD.DateTimeDigitized),
                exif_data.get('0th', {}).get(piexif.ImageIFD.DateTime)
            ]
            
            date_str = None
            for tag in date_tags:
                if tag:
                    date_str = tag.decode('utf-8') if isinstance(tag, bytes) else tag
                    break
            
            if date_str:
                # 解析日期字符串 (格式通常为 "YYYY:MM:DD HH:MM:SS")
                try:
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    # 只返回年月日
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # 如果解析失败，尝试其他格式或返回None
                    return None
            return None
        except Exception as e:
            print(f"获取EXIF日期时出错 ({image_path}): {e}")
            return None
    
    def _get_text_position(self, image_width, image_height, text_width, text_height):
        """根据用户选择的位置确定文本的坐标"""
        margin = 10  # 边距
        
        if self.position == 'top_left':
            return (margin, margin)
        elif self.position == 'top_center':
            return ((image_width - text_width) // 2, margin)
        elif self.position == 'top_right':
            return (image_width - text_width - margin, margin)
        elif self.position == 'middle_left':
            return (margin, (image_height - text_height) // 2)
        elif self.position == 'middle_center':
            return ((image_width - text_width) // 2, (image_height - text_height) // 2)
        elif self.position == 'middle_right':
            return (image_width - text_width - margin, (image_height - text_height) // 2)
        elif self.position == 'bottom_left':
            return (margin, image_height - text_height - margin)
        elif self.position == 'bottom_center':
            return ((image_width - text_width) // 2, image_height - text_height - margin)
        elif self.position == 'bottom_right':  # 默认位置
            return (image_width - text_width - margin, image_height - text_height - margin)
        else:
            # 如果位置参数无效，返回默认位置
            return (image_width - text_width - margin, image_height - text_height - margin)
    
    def _get_font(self):
        """尝试获取合适的字体"""
        # 尝试使用系统字体，这里提供了几种常见的字体名称作为备选
        font_names = ['Arial', 'SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'sans-serif']
        
        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, self.font_size)
            except (IOError, OSError):
                continue
        
        # 如果找不到指定的字体，使用默认字体
        return ImageFont.load_default()
    
    def add_watermark(self, image_path):
        """为单个图片添加水印"""
        try:
            # 打开图片
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # 获取EXIF日期作为水印文本
            watermark_text = self._get_exif_date(image_path)
            
            # 如果无法获取EXIF日期，使用当前日期作为备选
            if not watermark_text:
                watermark_text = datetime.now().strftime('%Y-%m-%d')
                print(f"警告: 无法从 {image_path} 获取EXIF日期，使用当前日期作为水印")
            
            # 获取字体
            font = self._get_font()
            
            # 获取文本尺寸
            text_width, text_height = draw.textsize(watermark_text, font=font)
            
            # 获取文本位置
            position = self._get_text_position(image.width, image.height, text_width, text_height)
            
            # 添加阴影效果，使水印更清晰可见
            shadow_color = (0, 0, 0, 128)  # 半透明黑色
            for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                draw.text(
                    (position[0] + offset[0], position[1] + offset[1]),
                    watermark_text,
                    font=font,
                    fill=shadow_color
                )
            
            # 添加主文本
            draw.text(position, watermark_text, font=font, fill=self.font_color)
            
            # 保存带水印的图片
            base_name = os.path.basename(image_path)
            output_path = os.path.join(self.output_dir, base_name)
            image.save(output_path)
            
            print(f"已成功为 {image_path} 添加水印并保存到 {output_path}")
            return True
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")
            return False
    
    def process_directory(self):
        """处理目录中的所有图片"""
        if os.path.isdir(self.image_path):
            # 支持的图片格式
            supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
            
            # 获取目录中的所有图片文件
            image_files = []
            for root, _, files in os.walk(self.image_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_formats):
                        image_files.append(os.path.join(root, file))
            
            if not image_files:
                print(f"在 {self.image_path} 中未找到支持的图片文件")
                return
            
            # 处理每个图片文件
            success_count = 0
            for image_file in image_files:
                if self.add_watermark(image_file):
                    success_count += 1
            
            print(f"处理完成! 成功为 {success_count} 张图片添加水印，保存至 {self.output_dir}")
        else:
            # 处理单个图片文件
            self.add_watermark(self.image_path)

def parse_color(color_str):
    """将颜色字符串解析为RGB元组"""
    if color_str.startswith('#'):
        # 处理十六进制颜色格式，如 #FF0000
        color_str = color_str.lstrip('#')
        if len(color_str) == 6:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b)
    elif ',' in color_str:
        # 处理RGB颜色格式，如 255,0,0
        try:
            parts = color_str.split(',')
            if len(parts) == 3:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                # 确保值在0-255范围内
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                return (r, g, b)
        except ValueError:
            pass
    
    # 如果解析失败，返回默认颜色（白色）
    return (255, 255, 255)

def main():
    # 定义命令行参数
    parser = argparse.ArgumentParser(description='为图片添加拍摄日期水印')
    parser.add_argument('path', help='图片文件路径或包含图片的目录路径')
    parser.add_argument('--font-size', type=int, default=24, help='水印字体大小（默认：24）')
    parser.add_argument('--color', default='255,255,255', help='水印颜色（支持格式：#FFFFFF 或 255,255,255，默认：白色）')
    parser.add_argument('--position', 
                        choices=['top_left', 'top_center', 'top_right', 
                                 'middle_left', 'middle_center', 'middle_right', 
                                 'bottom_left', 'bottom_center', 'bottom_right'],
                        default='bottom_right',
                        help='水印位置（默认：右下角）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 解析颜色参数
    font_color = parse_color(args.color)
    
    # 创建水印处理器并处理图片
    watermark_processor = ImageWatermark(
        args.path,
        font_size=args.font_size,
        font_color=font_color,
        position=args.position
    )
    
    watermark_processor.process_directory()

if __name__ == '__main__':
    main()