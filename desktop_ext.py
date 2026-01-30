import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

# =============================================================================
# [1] DATA ARCHITECTURE DEFINITION
# =============================================================================
# 保存用ディレクトリとコンフィグファイルの物理パスを確定させます。
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "app", "deta")
CONFIG_FILE = os.path.join(DATA_DIR, "desktop_ext_deta.qcfg")

# ディレクトリが存在しない場合の自動生成プロトコル
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
    except OSError:
        pass

def run(root, os_core):
    """Kernelからのエントリポイント"""
    DesktopExt(root, os_core)

class DesktopExt:
    """
    デスクトップ環境の拡張および設定の永続化を司るクラス。
    壁紙、アイコン配置、ユーザー設定を .qcfg ファイルと同期させます。
    """
    def __init__(self, master, os_core):
        self.os_core = os_core
        self.win = tk.Toplevel(master)
        self.win.title("QUORI 10 DESKTOP MANAGER")
        self.win.geometry("500x650")
        self.win.configure(bg="#0a0a0a")
        self.win.attributes("-topmost", True)
        
        # システム色の取得
        self.acc = self.os_core.config.get("accent_color", "#00d9ff")
        
        # --- 内部ステート変数 ---
        self.local_config = {
            "wallpaper_path": "",
            "icons_visible": False,
            "desktop_opacity": 1.0,
            "last_update": ""
        }
        
        # 1. 保存されたデータのロード
        self.load_desktop_data()
        
        # 2. ロードされたデータに基づき初期描画
        self.apply_stored_settings()
        
        # 3. UIコンポーネントの構築
        self.render_interface()

    # -------------------------------------------------------------------------
    # PERSISTENCE METHODS (SAVE/LOAD)
    # -------------------------------------------------------------------------
    def load_desktop_data(self):
        """desktop_ext_deta.qcfg から設定を読み込みます。"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    stored_data = json.load(f)
                    self.local_config.update(stored_data)
                self.os_core.write_log("Desktop Extension: Data loaded successfully.")
            except Exception as e:
                self.os_core.write_log(f"Desktop Extension: Load error - {e}")

    def save_desktop_data(self):
        """現在の設定を desktop_ext_deta.qcfg へ永続化します。"""
        try:
            import datetime
            self.local_config["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_config, f, indent=4)
            
            self.os_core.write_log("Desktop Extension: System state persisted.")
        except Exception as e:
            messagebox.showerror("STORAGE ERROR", f"Failed to save desktop data: {e}")

    # -------------------------------------------------------------------------
    # CORE LOGIC METHODS
    # -------------------------------------------------------------------------
    def apply_stored_settings(self):
        """起動時に保存されていた壁紙などを自動適用します。"""
        path = self.local_config.get("wallpaper_path")
        if path and os.path.exists(path):
            self._set_wallpaper_logic(path)
            
        if self.local_config.get("icons_visible"):
            self.render_icons()

    def render_interface(self):
        """管理ウィンドウのUIを構築します。"""
        # ヘッダー
        tk.Label(self.win, text="DESKTOP PERSISTENCE CONTROL", 
                 fg=self.acc, bg="#0a0a0a", font=("Consolas", 14, "bold")).pack(pady=30)

        # ステータス情報表示
        info_frame = tk.Frame(self.win, bg="#111", padx=10, pady=10)
        info_frame.pack(fill="x", padx=40, pady=10)
        
        tk.Label(info_frame, text=f"Data Path: app/deta/desktop_ext_deta.qcfg", 
                 fg="#666", bg="#111", font=("Consolas", 8)).pack(anchor="w")
        self.status_label = tk.Label(info_frame, text=f"Last Sync: {self.local_config['last_update']}", 
                                     fg="#888", bg="#111", font=("Consolas", 8))
        self.status_label.pack(anchor="w")

        # 操作ボタン群
        btn_style = {"bg": "#151515", "fg": "white", "relief": "flat", 
                     "font": ("Consolas", 10), "activebackground": self.acc, "pady": 12}
        
        tk.Button(self.win, text="🖼️ BROWSE & APPLY WALLPAPER", 
                  command=self.select_wallpaper, **btn_style, width=38).pack(pady=8)

        tk.Button(self.win, text="💠 TOGGLE DESKTOP ICONS", 
                  command=self.render_icons, **btn_style, width=38).pack(pady=8)

        # スペーサー
        tk.Frame(self.win, bg="#222", height=1).pack(fill="x", padx=50, pady=20)

        # リセットボタン（保存データも消去）
        tk.Button(self.win, text="🔄 FACTORY RESET & CLEAR DATA", 
                  command=self.factory_reset, bg="#111", fg="#ff3366", 
                  relief="flat", font=("Consolas", 10, "bold"), pady=12, width=38).pack(pady=8)

        # 閉じるボタン
        tk.Button(self.win, text="EXIT MANAGER", command=self.win.destroy, 
                  bg="#333", fg="white", relief="flat", width=20).pack(pady=40)

    def select_wallpaper(self):
        """ファイルダイアログから画像を選択し、保存します。"""
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self._set_wallpaper_logic(path)
            self.local_config["wallpaper_path"] = path
            self.save_desktop_data()
            self.status_label.config(text=f"Last Sync: {self.local_config['last_update']}")

    def _set_wallpaper_logic(self, path):
        """実際に背景ラベルに画像をセットする内部処理。"""
        try:
            img = Image.open(path).resize((self.os_core.sw, self.os_core.sh), Image.Resampling.LANCZOS)
            self.os_core.desktop_image_ref = ImageTk.PhotoImage(img)
            self.os_core.bg_label.config(image=self.os_core.desktop_image_ref, text="")
        except Exception as e:
            messagebox.showerror("IMG ERR", f"Failed to render: {e}")

    def factory_reset(self):
        """すべての設定を初期化し、保存ファイルもリセットします。"""
        if messagebox.askyesno("SYSTEM WARNING", "This will wipe all desktop settings. Continue?"):
            # Kernel側のリセット
            self.os_core.bg_label.config(image="", text="Quori OS 10 Core Online", fg="#0088ff")
            self.os_core.desktop_image_ref = None
            if hasattr(self.os_core, 'icon_group') and self.os_core.icon_group:
                self.os_core.icon_group.destroy()
                self.os_core.icon_group = None
            
            # 保存データの初期化
            self.local_config = {
                "wallpaper_path": "",
                "icons_visible": False,
                "desktop_opacity": 1.0,
                "last_update": ""
            }
            self.save_desktop_data()
            self.status_label.config(text="Last Sync: RESET")
            messagebox.showinfo("RESET COMPLETE", "Configuration file has been cleared.")

    def render_icons(self):
        """デスクトップ上にアイコンをレンダリングし、状態を保存します。"""
        if hasattr(self.os_core, 'icon_group') and self.os_core.icon_group:
            self.os_core.icon_group.destroy()
            self.local_config["icons_visible"] = False
        else:
            self.os_core.icon_group = tk.Frame(self.os_core.root, bg="", bd=0)
            self.os_core.icon_group.place(x=60, y=60)
            
            apps = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py")]
            for i, name in enumerate(apps):
                aid = name.replace(".py", "")
                btn = tk.Button(self.os_core.icon_group, text=f"💠\n{aid.upper()}", 
                                fg="white", bg="black", relief="flat", font=("Consolas", 10), 
                                width=12, command=lambda n=aid: self.os_core.invoke_app(n))
                btn.grid(row=i//5, column=i%5, padx=20, pady=20)
            self.local_config["icons_visible"] = True
            
        self.save_desktop_data()
