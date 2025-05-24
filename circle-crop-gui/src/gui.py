import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class CircleCropGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Circle Cropper")

        self.input_dir = None
        self.output_dir = None
        self.image_files = []
        self.current_image_index = 0

        self.image_label = tk.Label(master, text="No image selected")
        self.image_label.pack()

        self.canvas = tk.Canvas(master, width=400, height=400, bg='white')
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        self.delete_button = tk.Button(master, text="Delete Circle", command=self.delete_circle)
        self.delete_button.pack()

        self.center_x = tk.IntVar(value=200)
        self.center_y = tk.IntVar(value=200)
        self.radius = tk.IntVar(value=100)

        tk.Label(master, text="Center X:").pack()
        tk.Entry(master, textvariable=self.center_x).pack()
        tk.Label(master, text="Center Y:").pack()
        tk.Entry(master, textvariable=self.center_y).pack()
        tk.Label(master, text="Radius:").pack()
        tk.Entry(master, textvariable=self.radius).pack()

        self.image_path = None
        self.image = None
        self.circle = None
        self.start_x = None
        self.start_y = None
        self.circle_center = None
        self.circle_radius = None
        self.dragging = False
        self.resizing = False
        self.drag_offset = (0, 0)
        self.resize_start = None

        # 入力ディレクトリ表示＋選択ボタン
        dir_frame = tk.Frame(master)
        dir_frame.pack(pady=2)
        self.input_dir_var = tk.StringVar(value="(未選択)")
        self.input_dir_label = tk.Label(dir_frame, textvariable=self.input_dir_var, width=40, anchor="w")
        self.input_dir_label.pack(side=tk.LEFT)
        self.select_dir_button = tk.Button(dir_frame, text="Select Directory", command=self.select_directory)
        self.select_dir_button.pack(side=tk.LEFT)

        # 出力ディレクトリ表示＋選択ボタン
        out_frame = tk.Frame(master)
        out_frame.pack(pady=2)
        self.output_dir_var = tk.StringVar(value="(未選択)")
        self.output_dir_label = tk.Label(out_frame, textvariable=self.output_dir_var, width=40, anchor="w")
        self.output_dir_label.pack(side=tk.LEFT)
        self.select_output_dir_button = tk.Button(out_frame, text="Select Output Directory", command=self.select_output_directory)
        self.select_output_dir_button.pack(side=tk.LEFT)

        # 実行ボタン
        self.run_button = tk.Button(master, text="Run", command=self.run_crop)
        self.run_button.pack()

    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("JPEG files", "*.jpeg"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff"),
                ("All files", "*.*"),
            ]
        )
        if self.image_path:
            self.load_image()

    def load_image(self):
        self.image = Image.open(self.image_path)
        self.image.thumbnail((400, 400))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.image_label.config(text=os.path.basename(self.image_path))
        # 円もリセット
        self.circle = None

    def crop_image(self):
        if not self.input_dir or not self.image_files:
            messagebox.showwarning("Warning", "Please select a directory with images first.")
            return
        # サイズチェック
        from PIL import Image
        first_img = Image.open(os.path.join(self.input_dir, self.image_files[0]))
        base_size = first_img.size
        mismatched = []
        for fname in self.image_files:
            img = Image.open(os.path.join(self.input_dir, fname))
            if img.size != base_size:
                mismatched.append(fname)
        if mismatched:
            messagebox.showerror("Error", "以下の画像はサイズが一致しません:\n" + "\n".join(mismatched))
            return
        # 出力ディレクトリ選択
        output_dir = filedialog.askdirectory(title="Output Directory")
        if not output_dir:
            return
        # 一括切り抜き
        center = (self.center_x.get(), self.center_y.get())
        radius = self.radius.get()
        from image_utils import circular_crop
        for fname in self.image_files:
            input_path = os.path.join(self.input_dir, fname)
            output_path = os.path.join(output_dir, fname)
            try:
                circular_crop(input_path, output_path, center, radius, True)
            except Exception as e:
                messagebox.showerror("Error", f"{fname} の処理中にエラー: {e}")
                return
        messagebox.showinfo("Success", f"全{len(self.image_files)}枚の画像を一括切り抜きしました。")

    # --- ここからマウス操作による円選択 ---
    def on_canvas_press(self, event):
        if self.circle:
            # 円の中心との距離で「移動」か「リサイズ」か判定
            x0, y0, x1, y1 = self.canvas.coords(self.circle)
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            r = max(abs(x1 - x0), abs(y1 - y0)) / 2
            dist = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
            if abs(dist - r) < 10:
                self.resizing = True
                self.resize_start = (cx, cy)
            elif dist < r:
                self.dragging = True
                self.drag_offset = (event.x - cx, event.y - cy)
            else:
                # 新しい円を描く場合は既存の円を削除してから
                self.canvas.delete(self.circle)
                self.circle = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="red", width=2)
                self.circle_center = (event.x, event.y)
                self.circle_radius = 0
                self.dragging = False
                self.resizing = False
        else:
            # 新しい円を描く
            self.circle = self.canvas.create_oval(event.x, event.y, event.x, event.y, outline="red", width=2)
            self.circle_center = (event.x, event.y)
            self.circle_radius = 0

    def on_canvas_drag(self, event):
        if self.dragging and self.circle:
            # 円を移動
            cx, cy = event.x - self.drag_offset[0], event.y - self.drag_offset[1]
            r = self.circle_radius
            self.canvas.coords(self.circle, cx - r, cy - r, cx + r, cy + r)
            self.circle_center = (cx, cy)
        elif self.resizing and self.circle:
            # 半径を変更
            cx, cy = self.resize_start
            r = ((event.x - cx) ** 2 + (event.y - cy) ** 2) ** 0.5
            self.canvas.coords(self.circle, cx - r, cy - r, cx + r, cy + r)
            self.circle_radius = r
        elif self.circle:
            # 新規作成時
            r = ((event.x - self.circle_center[0]) ** 2 + (event.y - self.circle_center[1]) ** 2) ** 0.5
            cx, cy = self.circle_center
            self.canvas.coords(self.circle, cx - r, cy - r, cx + r, cy + r)
            self.circle_radius = r

    def on_canvas_release(self, event):
        self.dragging = False
        self.resizing = False
        # Entryにも反映
        if self.circle_center and self.circle_radius is not None:
            self.center_x.set(int(self.circle_center[0]))
            self.center_y.set(int(self.circle_center[1]))
            self.radius.set(int(self.circle_radius))

    def delete_circle(self):
        if self.circle:
            self.canvas.delete(self.circle)
            self.circle = None
            self.circle_center = None
            self.circle_radius = None
            # Entryもリセット
            self.center_x.set(0)
            self.center_y.set(0)
            self.radius.set(0)

    def select_directory(self):
        input_dir = filedialog.askdirectory(title="Input Directory")
        if not input_dir:
            return
        self.input_dir = input_dir
        self.input_dir_var.set(input_dir)
        exts = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
        self.image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(exts)]
        if not self.image_files:
            messagebox.showerror("Error", "No image files found in the selected directory.")
            return
        # 最初の画像を表示
        self.current_image_index = 0
        self.image_path = os.path.join(self.input_dir, self.image_files[0])
        self.load_image()

    def select_output_directory(self):
        output_dir = filedialog.askdirectory(title="Output Directory")
        if not output_dir:
            return
        self.output_dir = output_dir
        self.output_dir_var.set(output_dir)

    def run_crop(self):
        if not self.input_dir or not self.output_dir or not self.image_files:
            messagebox.showwarning("Warning", "Please select both input and output directories.")
            return
        # サイズチェック
        from PIL import Image
        first_img = Image.open(os.path.join(self.input_dir, self.image_files[0]))
        base_size = first_img.size
        mismatched = []
        for fname in self.image_files:
            img = Image.open(os.path.join(self.input_dir, fname))
            if img.size != base_size:
                mismatched.append(fname)
        if mismatched:
            messagebox.showerror("Error", "以下の画像はサイズが一致しません:\n" + "\n".join(mismatched))
            return

        # キャンバスと元画像のスケール比を計算
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_w, img_h = base_size
        scale_x = img_w / canvas_w
        scale_y = img_h / canvas_h

        # 一括切り抜き
        center_canvas = (self.center_x.get(), self.center_y.get())
        radius_canvas = self.radius.get()
        # スケール変換
        center = (int(center_canvas[0] * scale_x), int(center_canvas[1] * scale_y))
        radius = int(radius_canvas * (scale_x + scale_y) / 2)  # 平均スケール

        from image_utils import circular_crop
        for fname in self.image_files:
            input_path = os.path.join(self.input_dir, fname)
            output_path = os.path.join(self.output_dir, fname)
            try:
                circular_crop(input_path, output_path, center, radius, True)
            except Exception as e:
                messagebox.showerror("Error", f"{fname} の処理中にエラー: {e}")
                return
        messagebox.showinfo("Success", f"全{len(self.image_files)}枚の画像を一括切り抜きしました。")

def create_gui(root, input_path, output_dir, center, radius, remove_transparent_bg, on_crop_button_click, on_crop_directory_button_click):
    app = CircleCropGUI(root)
    # 一括ディレクトリ切り抜きボタンを追加
    def select_and_crop_directory():
        input_dir = filedialog.askdirectory(title="Input Directory")
        if not input_dir:
            return
        output_dir = filedialog.askdirectory(title="Output Directory")
        if not output_dir:
            return
        # 現在のGUIの値を取得
        center_val = (app.center_x.get(), app.center_y.get())
        radius_val = app.radius.get()
        on_crop_directory_button_click(
            input_dir, output_dir, center_val, radius_val, remove_transparent_bg
        )    
    return app

if __name__ == "__main__":
    root = tk.Tk()
    app = CircleCropGUI(root)
    root.mainloop()