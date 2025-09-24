# 图片水印工具

一个简单的命令行程序，用于为图片添加基于EXIF拍摄日期的水印。

## 功能特点

- 读取图片的EXIF信息中的拍摄时间，提取年月日作为水印文本
- 支持自定义水印的字体大小、颜色和位置
- 可以处理单个图片或整个目录中的所有图片
- 自动创建输出目录保存带水印的图片
- 添加阴影效果使水印更清晰可见

## 安装依赖

使用以下命令安装所需的Python包：

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行参数

```
python watermark.py <path> [--font-size SIZE] [--color COLOR] [--position POSITION]
```

- `path`: 图片文件路径或包含图片的目录路径（必填）
- `--font-size`: 水印字体大小（默认：24）
- `--color`: 水印颜色（支持格式：#FFFFFF 或 255,255,255，默认：白色）
- `--position`: 水印位置（可选值如下，默认：右下角）
  - top_left: 左上角
  - top_center: 上中
  - top_right: 右上角
  - middle_left: 左中
  - middle_center: 居中
  - middle_right: 右中
  - bottom_left: 左下角
  - bottom_center: 下中
  - bottom_right: 右下角

### 示例

处理单个图片：

```bash
python watermark.py example.jpg --font-size 36 --color 255,0,0 --position bottom_right
```

处理整个目录中的所有图片：

```bash
python watermark.py ./photos_folder --font-size 24 --color #FFFF00 --position bottom_center
```

## 输出

处理后的图片将保存在原目录下的 `<原目录名>_watermark` 子目录中。

例如：如果原图片路径为 `D:\photos\example.jpg`，则处理后的图片将保存在 `D:\photos\photos_watermark\example.jpg`。

## 注意事项

1. 如果图片没有EXIF拍摄日期信息，程序将使用当前日期作为水印文本
2. 程序支持常见的图片格式：jpg、jpeg、png、bmp、gif、tiff
3. 为了确保中文字体能正常显示，程序会尝试加载系统中可用的中文字体

## 系统要求

- Python 3.6+