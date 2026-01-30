import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil

def run(main_root, os_core):
    """
    OSコアのデスクトップ・レイヤーを直接書き換え、
    ファイル表示機能と背景カスタマイズ機能を提供します。
    """
    DesktopExtension(main_root, os_core)

class DesktopExtension:
    def __init__(self, master, os_core):
        self.master = master
        self.os_core = os_core
        self.acc = self.os_core.config.get("accent_color", "#00d9ff")
        
        # 設定ウィンドウの展開
        self.win = tk.Toplevel(master)
        self.win.title("DESKTOP ENHANCER")
        self.win.geometry("400x300")
        self.win.configure(bg="#0a0a0a")
        self.win.attributes("-topmost", True)
        
        tk.Label(self.win, text="DESKTOP EXTENSION v1.0", fg=self.acc, bg="#0a0a0a", 
                 font=("Consolas", 12, "bold")).pack(pady=20)

        # 背景画像変更ボタン
        tk.Button(self.win, text="CHANGE WALLPAPER (IMG)", command=self.change_wallpaper,
                  bg="#111", fg="white", relief="flat", padx=20, pady=10).pack(fill="x", padx=50, pady=5)
        
        # ファイル表示の有効化
        tk.Button(self.win, text="RENDER DESKTOP FILES", command=self.render_files,
                  bg="#111", fg="white", relief="flat", padx=20, pady=10).pack(fill="x", padx=50, pady=5)

        tk.Label(self.win, text="*Wallpaper resets to logo.png by default", 
                 fg="#555", bg="#0a0a0a", font=("Consolas", 8)).pack(pady=20)

    def change_wallpaper(self):
        """
        選択した画像をロゴとして上書き、またはデスクトップ背景として即時反映させます。
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if not file_path:
            return

        try:
            # 画像を画面サイズに合わせてリサイズし、boost.pyの背景ラベルを更新
            img = Image.open(file_path)
            sw, sh = self.os_core.sw, self.os_core.sh
            img = img.resize((sw, sh), Image.Resampling.LANCZOS)
            
            self.os_core.desktop_bg_img = ImageTk.PhotoImage(img)
            
            # boost.pyの背景ラベルを画像モードへ切り替え
            if hasattr(self.os_core, 'bg_label'):
                self.os_core.bg_label.config(image=self.os_core.desktop_bg_img, text="")
                # 中央配置
                self.os_core.bg_label.place(relx=0.5, rely=0.5, anchor="center")
            
            messagebox.showinfo("SUCCESS", "Wallpaper updated successfully.")
        except Exception as e:
            messagebox.showerror("ERROR", f"Failed to apply wallpaper: {e}")

    def render_files(self):
        """
        デスクトップ上にアイコン（ボタン）としてapp内のファイルを表示します。
        """
        # すでに表示されているアイコンがあれば掃除（再描画用）
        if hasattr(self, 'icon_frame'):
            self.icon_frame.destroy()
            
        self.icon_frame = tk.Frame(self.master, bg="", bd=0)
        self.icon_frame.place(x=50, y=50) # デスクトップ左上に配置
        
        app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        
        # appフォルダ内のファイルを取得
        files = [f for f in os.listdir(app_dir) if f.endswith(".py")]
        
        for i, f_name in enumerate(files):
            # アイコン風のボタンを作成
            btn = tk.Button(self.icon_frame, text=f"📄\n{f_name}", 
                           fg="white", bg="black", relief="flat", 
                           font=("Consolas", 8), width=10,
                           command=lambda n=f_name.replace(".py", ""): self.os_core.launch_app(n))
            # グリッド配置 (縦に並べる)
            btn.grid(row=i % 5, column=i // 5, padx=10, pady=10)
            
            # ホバーエフェクト
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#222"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="black"))

        messagebox.showinfo("DESKTOP", "File icons rendered on desktop layer.")
