#pyinstaller --noconsole --onefile ChroLens_Sentinel.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
import json
import os
import pystray
from PIL import Image, ImageDraw
from update_manager import UpdateManager
from update_dialog import UpdateDialog, NoUpdateDialog

# 版本管理模組
try:
    from version_manager import VersionManager
    from version_info_dialog import VersionInfoDialog
    VERSION_MANAGER_AVAILABLE = True
except ImportError:
    print("版本管理模組未安裝，版本檢查功能將停用")
    VERSION_MANAGER_AVAILABLE = False


CURRENT_VERSION = "1.0"
GITHUB_REPO = "Lucienwooo/ChroLens_Sentinel"
DEFAULT_FILES = ["MSBuild.exe", "RegAsm.exe", "RegSvcs.exe", "AddInUtil.exe", "aspnet_compiler.exe"]
SAVE_FILE = "ChroLens_Sentinel_settings.json"

class ChroLens_SentinelApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"ChroLens_Sentinel {CURRENT_VERSION}")
        self.style = tb.Style("darkly")
        self.file_vars = []
        self.entries = []
        self.running = False
        self.icon = None  # 系統匣圖示物件

        main_frame = tb.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tb.Label(main_frame, text="強制關閉：", font=("微軟正黑體", 12)).pack(anchor='w', pady=(0, 6))

        self.list_frame = tb.Frame(main_frame)
        self.list_frame.pack(fill="x", pady=(0, 8))

        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 8))
        tb.Button(btn_frame, text="新增欄位", command=self.add_file_entry, bootstyle="success").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="刪除欄位", command=self.remove_file_entry, bootstyle="danger").pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="儲存", command=self.save_settings, bootstyle="warning").pack(side=LEFT, padx=5)

        interval_row = tb.Frame(main_frame)
        interval_row.pack(fill="x", pady=(0, 8))
        tb.Label(interval_row, text="封鎖間隔（分鐘）：").pack(side=LEFT)
        self.interval_var = tk.StringVar(value="60")
        tb.Entry(interval_row, textvariable=self.interval_var, width=8).pack(side=LEFT, padx=5)

        status_row = tb.Frame(main_frame)
        status_row.pack(fill="x", pady=(0, 8))
        tb.Label(status_row, text="目前狀態：").pack(side=LEFT)
        self.status_var = tk.StringVar(value="已停止")
        tb.Label(status_row, textvariable=self.status_var, foreground="green").pack(side=LEFT, padx=5)

        action_row = tb.Frame(main_frame)
        action_row.pack(fill="x", pady=(0, 8))
        tb.Button(action_row, text="啟動自動封鎖", command=self.start_block, bootstyle="primary").pack(side=LEFT, padx=5)
        tb.Button(action_row, text="停止封鎖", command=self.stop_block, bootstyle="secondary").pack(side=LEFT, padx=5)
        tb.Button(action_row, text="關於", command=self.show_about, bootstyle="info").pack(side=LEFT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Unmap>", self.on_minimize)  # 監聽縮小事件

        self.load_settings()

    def create_tray_icon(self):
        # 建立一個簡單的圖示
        image = Image.new('RGB', (64, 64), color=(40, 40, 40))
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill=(0, 180, 255))
        menu = pystray.Menu(
            pystray.MenuItem('還原視窗', self.show_window),
            pystray.MenuItem('結束程式', self.exit_app)
        )
        self.icon = pystray.Icon("CL_Sentinel", image, "CL_Sentinel", menu)

        # 設定雙擊事件
        def on_double_click(icon, item=None):
            self.show_window(icon, item)
        self.icon.on_double_click = on_double_click

        threading.Thread(target=self.icon.run, daemon=True).start()

    def on_minimize(self, event):
        if self.root.state() == "iconic":
            self.root.withdraw()
            if self.icon is None:
                self.create_tray_icon()

    def show_window(self, icon, item):
        self.root.deiconify()
        self.root.state("normal")
        if self.icon:
            self.icon.stop()
            self.icon = None

    def exit_app(self, icon, item):
        self.on_close()

    def update_window_height(self):
        base_height = 250
        extra_height = max(0, len(self.entries) * 40)
        self.root.geometry(f"300x{base_height + extra_height}")

    def add_file_entry(self, value=""):
        var = tk.StringVar(value=value)
        row = tb.Frame(self.list_frame)
        row.pack(fill="x", pady=2)
        entry = tb.Entry(row, textvariable=var, width=32, font=("微軟正黑體", 10))
        entry.pack(side=LEFT, padx=5)
        self.file_vars.append(var)
        self.entries.append(row)
        self.update_window_height()

    def remove_file_entry(self):
        if self.entries:
            row = self.entries.pop()
            row.destroy()
            self.file_vars.pop()
            self.update_window_height()

    def get_file_list(self):
        return [v.get().strip() for v in self.file_vars if v.get().strip()]

    def block_files(self):
        files = self.get_file_list()
        for exe in files:
            subprocess.run(f"taskkill /f /im {exe}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def auto_block_loop(self, interval):
        while self.running:
            self.block_files()
            time.sleep(interval * 60)

    def start_block(self):
        if self.running:
            messagebox.showinfo("提示", "自動封鎖已在運行中")
            return
        try:
            interval = int(self.interval_var.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的分鐘數")
            return
        self.running = True
        threading.Thread(target=self.auto_block_loop, args=(interval,), daemon=True).start()
        self.status_var.set("運行中")
        messagebox.showinfo("啟動", f"已啟動自動封鎖（每 {interval} 分鐘執行一次）")

    def stop_block(self):
        self.running = False
        self.status_var.set("已停止")
        messagebox.showinfo("停止", "已停止自動封鎖")

    def save_settings(self, silent=False):
        data = {
            "interval": self.interval_var.get(),
            "files": self.get_file_list(),
            "count": len(self.entries)
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            if not silent:
                messagebox.showinfo("儲存成功", "設定已儲存")
        except Exception as e:
            if not silent:
                messagebox.showerror("儲存失敗", str(e))

    def load_settings(self):
        if not os.path.exists(SAVE_FILE):
            # 預設5個欄位
            for i in range(5):
                self.add_file_entry(DEFAULT_FILES[i] if i < len(DEFAULT_FILES) else "")
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.interval_var.set(data.get("interval", "60"))
            files = data.get("files", [])
            # 清空現有欄位
            for row in self.entries:
                row.destroy()
            self.entries.clear()
            self.file_vars.clear()
            for name in files:
                self.add_file_entry(name)
            # 若欄位不足，補足到原本數量
            count = data.get("count", 5)
            while len(self.entries) < count:
                self.add_file_entry("")
        except Exception as e:
            messagebox.showerror("載入失敗", str(e))

    def show_about(self):
        """顯示關於視窗"""
        about_win = tb.Toplevel(self.root)
        about_win.title("關於 ChroLens_Sentinel")
        about_win.geometry("450x300")
        about_win.resizable(False, False)
        about_win.grab_set()
        
        # 置中
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + 80
        about_win.geometry(f"+{x}+{y}")
        
        frm = tb.Frame(about_win, padding=20)
        frm.pack(fill="both", expand=True)
        
        tb.Label(frm, text=f"ChroLens_Sentinel {CURRENT_VERSION}", font=("Microsoft JhengHei", 14, "bold")).pack(anchor="w", pady=(0, 10))
        tb.Label(frm, text="定時關閉與封鎖指定程式\n防止背景偷跑佔用資源", font=("Microsoft JhengHei", 11)).pack(anchor="w", pady=(0, 16))
        
        link = tk.Label(frm, text="ChroLens_模擬器討論區", font=("Microsoft JhengHei", 10, "underline"), fg="#5865F2", cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda e: os.startfile("https://discord.gg/72Kbs4WPPn"))
        
        github = tk.Label(frm, text="查看更多工具(巴哈)", font=("Microsoft JhengHei", 10, "underline"), fg="#24292f", cursor="hand2")
        github.pack(anchor="w", pady=(8, 0))
        github.bind("<Button-1>", lambda e: os.startfile("https://home.gamer.com.tw/profile/index_creation.php?owner=umiwued&folder=523848"))
        
        tb.Label(frm, text="Created By Lucienwooo", font=("Microsoft JhengHei", 10)).pack(anchor="w", pady=(16, 0))
        
        # 檢查更新功能
        def check_for_updates():
            def update_check_thread():
                try:
                    updater = UpdateManager(CURRENT_VERSION)
                    update_info = updater.check_for_updates()
                    
                    if update_info:
                        about_win.after(0, lambda: UpdateDialog(self.root, updater, update_info))
                    else:
                        about_win.after(0, lambda: NoUpdateDialog(about_win, CURRENT_VERSION))
                except Exception as e:
                    about_win.after(0, lambda: messagebox.showerror("錯誤", f"檢查更新失敗：{str(e)}"))
            
            threading.Thread(target=update_check_thread, daemon=True).start()
        
        # 按鈕容器
        btn_frame = tb.Frame(frm)
        btn_frame.pack(anchor="e", pady=(16, 0))
        tb.Button(btn_frame, text="檢查更新", command=check_for_updates, width=10, bootstyle="info").pack(side=LEFT, padx=(0, 8))
        tb.Button(btn_frame, text="關閉", command=about_win.destroy, width=8, bootstyle="secondary").pack(side=LEFT)

    def on_close(self):
        self.running = False
        self.save_settings(silent=True)
        if self.icon:
            self.icon.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window()
    app = ChroLens_SentinelApp(root)
    root.mainloop()
