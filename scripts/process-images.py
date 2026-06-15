"""
图片处理脚本
将 image-original 中的原图压缩后输出到 images 文件夹

用法：
    python scripts/process-images.py

规则：
    - 长边最大 2000px
    - JPG 质量 80
    - 保留原始宽高比
    - 如果 images 中已有同名文件则跳过
    - image-original 中的原图不直接用于网页展示
"""

import os
from PIL import Image

SOURCE_DIR = "image-original"
TARGET_DIR = "images"
MAX_SIZE = 2000
QUALITY = 80

os.makedirs(SOURCE_DIR, exist_ok=True)
os.makedirs(TARGET_DIR, exist_ok=True)

processed = 0
skipped = 0
errors = []

for filename in os.listdir(SOURCE_DIR):
    src_path = os.path.join(SOURCE_DIR, filename)
    if not os.path.isfile(src_path):
        continue

    # 只处理图片格式
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif', '.bmp'):
        continue

    # 目标文件名统一为 .jpg
    target_name = os.path.splitext(filename)[0] + '.jpg'
    target_path = os.path.join(TARGET_DIR, target_name)

    if os.path.exists(target_path):
        skipped += 1
        print(f"跳过（已存在）: {target_name}")
        continue

    try:
        img = Image.open(src_path)

        # RGB转换（PNG可能有透明通道）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        width, height = img.size

        # 长边限制为 MAX_SIZE，等比缩放
        if width >= height:
            if width > MAX_SIZE:
                ratio = MAX_SIZE / width
                new_size = (MAX_SIZE, int(height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
        else:
            if height > MAX_SIZE:
                ratio = MAX_SIZE / height
                new_size = (int(width * ratio), MAX_SIZE)
                img = img.resize(new_size, Image.LANCZOS)

        img.save(target_path, 'JPEG', quality=QUALITY, optimize=True)
        processed += 1
        print(f"处理完成: {filename} → {target_name} ({img.size[0]}×{img.size[1]})")

    except Exception as e:
        errors.append((filename, str(e)))
        print(f"错误: {filename} - {e}")

print(f"\n--- 完成 ---")
print(f"处理: {processed} 张")
print(f"跳过: {skipped} 张")
if errors:
    print(f"错误: {len(errors)} 张")
    for fn, err in errors:
        print(f"  {fn}: {err}")