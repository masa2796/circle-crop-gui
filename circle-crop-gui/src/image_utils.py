import os
from PIL import Image, ImageDraw

def circular_crop(input_path, output_path, center=None, radius=None, remove_transparent_bg=False):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size

    if center is None:
        center = (width // 2, height // 2)
    if radius is None:
        radius = min(width, height) // 2

    # --- アンチエイリアス用に8倍サイズでマスクを作成 ---
    scale = 8
    mask_size = (width * scale, height * scale)
    mask = Image.new('L', mask_size, 0)
    draw = ImageDraw.Draw(mask)
    # 8倍スケールで円を描く
    draw.ellipse(
        (
            (center[0] - radius) * scale,
            (center[1] - radius) * scale,
            (center[0] + radius) * scale,
            (center[1] + radius) * scale
        ),
        fill=255
    )
    # オプション: さらにぼかす
    # from PIL import ImageFilter
    # mask = mask.filter(ImageFilter.GaussianBlur(radius=scale//2))

    # 元サイズに縮小（アンチエイリアス有効）
    mask = mask.resize((width, height), resample=Image.LANCZOS)

    circular_img = Image.new("RGBA", (width, height))
    circular_img.paste(img, (0, 0), mask=mask)

    if remove_transparent_bg:
        bbox = mask.getbbox()
        if bbox:
            circular_img = circular_img.crop(bbox)

    circular_img.save(output_path)

def process_directory(input_dir, output_dir, center=None, radius=None, remove_transparent_bg=False):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            output_path = os.path.join(output_dir, filename)
            circular_crop(input_path, output_path, center, radius, remove_transparent_bg)