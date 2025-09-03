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

DEFAULT_FILES = ["MSBuild.exe", "RegAsm.exe", "RegSvcs.exe", "AddInUtil.exe", "aspnet_compiler.exe"]
SAVE_FILE = "ChroLens_Sentinel_settings.json"

class ChroLens_SentinelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CL_Sentinel")
        self.style = tb.Style("darkly")
        self.file_vars = []
        self.entries = []
        self.running = False

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

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.load_settings()

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

    def on_close(self):
        self.running = False
        self.save_settings(silent=True)  # 關閉時不顯示提示視窗
        self.root.destroy()

if __name__ == "__main__":
    root = tb.Window()
    app = ChroLens_SentinelApp(root)
    root.mainloop()
