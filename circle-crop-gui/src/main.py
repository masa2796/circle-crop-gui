import tkinter as tk
from tkinter import messagebox
from gui import create_gui
from image_utils import circular_crop
import os

def process_image(input_path, output_path, center, radius, remove_transparent_bg):
    try:
        circular_crop(input_path, output_path, center, radius, remove_transparent_bg)
        messagebox.showinfo("Success", f"Processed: {input_path} -> {output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_crop_button_click(input_path, output_dir, center, radius, remove_transparent_bg):
    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Please select a valid image file.")
        return
    
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename)
    process_image(input_path, output_path, center, radius, remove_transparent_bg)

def on_crop_directory_button_click(input_dir, output_dir, center, radius, remove_transparent_bg):
    # ディレクトリ選択
    if not input_dir or not os.path.isdir(input_dir):
        messagebox.showerror("Error", "Please select a valid input directory.")
        return

    # 画像ファイル一覧取得
    exts = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(exts)]
    if not files:
        messagebox.showerror("Error", "No image files found in the selected directory.")
        return

    # 最初の画像サイズを基準にする
    from PIL import Image
    first_img = Image.open(os.path.join(input_dir, files[0]))
    base_size = first_img.size

    # サイズチェック
    mismatched = []
    for fname in files:
        img = Image.open(os.path.join(input_dir, fname))
        if img.size != base_size:
            mismatched.append(fname)
    if mismatched:
        messagebox.showerror("Error", "以下の画像はサイズが一致しません:\n" + "\n".join(mismatched))
        return

    # 出力ディレクトリ作成
    os.makedirs(output_dir, exist_ok=True)

    # 一括処理
    for fname in files:
        input_path = os.path.join(input_dir, fname)
        output_path = os.path.join(output_dir, fname)
        try:
            circular_crop(input_path, output_path, center, radius, remove_transparent_bg)
        except Exception as e:
            messagebox.showerror("Error", f"{fname} の処理中にエラー: {e}")
            return
    messagebox.showinfo("Success", f"全{len(files)}枚の画像を一括切り抜きしました。")

def main():
    root = tk.Tk()
    root.title("Circle Crop GUI")
    
    input_path = ""
    output_dir = "output_images"
    center = (1604, 112)  # Default center, can be updated via GUI
    radius = 47  # Default radius, can be updated via GUI
    remove_transparent_bg = True  # Default option

    # create_guiを拡張してディレクトリ一括ボタンを追加する場合は、gui.py側も修正してください
    create_gui(
        root, input_path, output_dir, center, radius, remove_transparent_bg,
        on_crop_button_click, on_crop_directory_button_click
    )

    root.mainloop()

if __name__ == "__main__":
    main()