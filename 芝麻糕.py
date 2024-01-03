import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import random
from ctypes import windll

# 自定义Canvas类，用于创建透明的画布
class TransparentCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.config(bg="white", highlightthickness=0, borderwidth=0)
        self.master = master

# 主应用程序类
class DesktopPet(tk.Tk):
    def __init__(self, gif_path):
        super().__init__()

        # 窗口标题和属性设置
        self.title("芝麻糕")
        self.overrideredirect(True)  # 隐藏标题栏和边框
        self.attributes("-transparent", "white")  # 设置透明色为白色
        self.attributes("-topmost", True)  # 始终显示在最顶层

        # 获取桌面尺寸
        desktop_width = windll.user32.GetSystemMetrics(0)
        desktop_height = windll.user32.GetSystemMetrics(1)

        self.geometry(f"{desktop_width}x{desktop_height}+0+0")  # 设置窗口大小为桌面大小，并位于左上角

        # 初始化变量
        self.gif_path = gif_path
        self.gif_frames = self.load_gif_frames(self.gif_path)
        self.current_frame = 0
        self.click_time = None
        self.click_timer_id = None
        self.dialog = None
        self.dialog_allowed = True

        # 创建界面组件
        self.create_widgets()

    # 创建界面组件的方法
    def create_widgets(self):
        # 创建透明画布
        self.canvas = TransparentCanvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.canvas.pack()

        # 在画布中心创建宠物图像
        pet_x = self.winfo_screenwidth() // 2
        pet_y = self.winfo_screenheight() // 2
        self.pet_id = self.canvas.create_image(pet_x, pet_y, anchor=tk.CENTER, image=self.gif_frames[0])

        # 绑定宠物图像事件
        self.canvas.tag_bind(self.pet_id, '<Button-1>', self.on_pet_click)
        self.canvas.tag_bind(self.pet_id, '<B1-Motion>', self.on_drag)

        # 定时调用方法
        self.after(15000, self.schedule_random_dialog)
        self.after(100, self.update_animation)

        # 创建按钮容器
        self.button_canvas = TransparentCanvas(self, width=100, height=40)
        button_window_x = pet_x - 180
        button_window_y = pet_y + 140
        self.button_canvas.place(x=button_window_x, y=button_window_y)

        # 创建按钮样式
        button_style = ttk.Style()

        # 定义按钮样式
        button_style.configure("Transparent.TButton",
                               background='#255277',    #设置按钮边框颜色
                               borderwidth=0,        # 设置边框宽度
                               highlightthickness=0)  # 设置高亮厚度

        # 添加按钮
        exit_button = ttk.Button(self.button_canvas, text="退出", command=self.quit, style="Transparent.TButton")
        exit_button.pack(side=tk.LEFT, padx=10)

        pet_button = ttk.Button(self.button_canvas, text="抚摸", command=self.pet_pat, style="Transparent.TButton")
        pet_button.pack(side=tk.LEFT, padx=10)

        talk_button = ttk.Button(self.button_canvas, text="你想知道什么？", command=self.talk_pat, style="Transparent.TButton")
        talk_button.pack(side=tk.LEFT, padx=10)
        
        # 创建对话框
        self.dialog = tk.Toplevel(self)
        self.dialog.title("对话框")
        self.dialog.withdraw()
        self.dialog_label = tk.Label(self.dialog, padx=10, pady=10)
        self.dialog_label.pack()

        # 绑定事件
        self.canvas.bind('<B1-Motion>', self.update_button_window_position)

    # 加载GIF图像的帧
    def load_gif_frames(self, path):
        gif = Image.open(path)
        gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
        return gif_frames

    # 更新宠物动画
    def update_animation(self):
        try:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.canvas.itemconfig(self.pet_id, image=self.gif_frames[self.current_frame])
            self.after(30, self.update_animation)
        except tk.TclError:
            pass

    # 处理宠物图像点击事件
    def on_pet_click(self, event):
        if self.click_timer_id is not None:
            self.after_cancel(self.click_timer_id)

        current_time = self.after(0)
        self.click_time = current_time

        self.show_dialog_wrapper()

    # 处理宠物图像拖动事件
    def on_drag(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.pet_id, x, y)

        if self.dialog.winfo_ismapped():
            dialog_x = x + 140
            dialog_y = y - 140
            self.dialog.geometry(f"+{int(dialog_x)}+{int(dialog_y)}")

    # 更新按钮窗口位置
    def update_button_window_position(self, event):
        x, y = event.x, event.y

        button_window_x = x - 100
        button_window_y = y + 140
        self.button_canvas.place(x=button_window_x, y=button_window_y)

    # 定时弹出随机对话
    def schedule_random_dialog(self):
        if self.dialog_allowed:
            if self.dialog:
                self.dialog.withdraw()

            random_message = random.choice(["邀诸位共赏", "人有五名，代价有三个", "我记得你，小姑娘"])
            self.show_dialog(random_message, duration=2000)

        self.after(15000, self.schedule_random_dialog)

    # 弹出对话框
    def show_dialog_wrapper(self):
        self.show_dialog("嗯？", duration=3000)

    # 显示对话框
    def show_dialog(self, custom_text=None, duration=5000):
        if custom_text:
            message = custom_text
        else:
            messages = ["邀诸位共赏", "人有五名，代价有三个", "我记得你，小姑娘"]
            message = random.choice(messages)

        pet_x, pet_y = self.canvas.coords(self.pet_id)
        dialog_x = pet_x + 140
        dialog_y = pet_y - 140
        self.dialog.geometry(f"+{int(dialog_x)}+{int(dialog_y)}")
        self.dialog_label.config(text=message)
        self.dialog.deiconify()
        self.dialog_allowed = False
        self.after(duration, self.reset_dialog_flag)

    # 重置对话框标志
    def reset_dialog_flag(self):
        if self.dialog and self.dialog.winfo_exists():
            self.after(100, self.hide_dialog)
        else:
            self.dialog_allowed = True

    # 隐藏对话框
    def hide_dialog(self):
        self.dialog.withdraw()
        self.dialog_allowed = True

    # 未实现的宠物抚摸方法
    def pet_pat(self):
        pass

    # 未实现的宠物交流方法
    def talk_pat(self):
        pass

if __name__ == "__main__":
    # 创建DesktopPet应用并运行
    pet_app = DesktopPet("C:/Users/Lenovo/Desktop/blade_desktop_pet/blade.gif")
    pet_app.mainloop()
