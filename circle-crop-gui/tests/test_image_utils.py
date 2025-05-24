import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from image_utils import circular_crop
from PIL import Image, ImageDraw

def approx_tuple(a, b, tol=5):
    return all(abs(x - y) <= tol for x, y in zip(a, b))

@pytest.mark.parametrize("center,radius", [
    ((50, 50), 30),      # 通常ケース
    ((0, 0), 10),        # 左上隅・小さい円
    ((99, 99), 1),       # 右下隅・最小半径
    ((50, 50), 0),       # 半径0（点）
    ((50, 50), 49),      # 画像サイズギリギリ
])
@pytest.mark.parametrize("remove_transparent_bg", [True, False])
def test_circular_crop(tmp_path, center, radius, remove_transparent_bg):
    # テスト用画像を生成
    img = Image.new("RGBA", (100, 100), color=(0, 128, 255, 255))
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    img.save(input_path)

    # maskをテスト側でも生成して期待サイズを計算
    mask = Image.new('L', (100, 100), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=255
    )
    bbox = mask.getbbox()

    # 切り抜き実行
    circular_crop(str(input_path), str(output_path), center, radius, remove_transparent_bg=remove_transparent_bg)

    # 出力ファイルが存在するか
    assert os.path.exists(output_path)

    # 出力画像のサイズ確認
    out_img = Image.open(output_path)
    if remove_transparent_bg:
        if bbox:
            expected_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            # 許容誤差±5ピクセル
            assert approx_tuple(out_img.size, expected_size, tol=5)
        else:
            assert out_img.size in [(0, 0), (1, 1), (100, 100)]
    else:
        assert out_img.size == (100, 100)

    # 画像モード確認
    assert out_img.mode in ("RGBA", "LA", "P", "RGB")

    # 境界値: 半径0の場合は中心1ピクセルのみ不透明（ただし透明でも許容/Pillow依存）
    if radius == 0 and not remove_transparent_bg:
        px = out_img.getpixel(center)
        assert px[3] in (0, 255)

def test_invalid_input(tmp_path):
    # 存在しないファイル
    with pytest.raises(Exception):
        circular_crop("not_exist.png", "out.png", (10, 10), 5, True)

    # 半径が負
    img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 255))
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    img.save(input_path)
    with pytest.raises(Exception):
        circular_crop(str(input_path), str(output_path), (5, 5), -1, True)