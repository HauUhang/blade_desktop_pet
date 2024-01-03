import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
from ctypes import windll

class DesktopPet(tk.Tk):
    def __init__(self, gif_path):
        super().__init__()

        self.title("芝麻糕") 
        self.overrideredirect(True)
        self.attributes("-transparent", "white") # 背景设置
        self.attributes("-topmost", True)  # 保持在最前面

        desktop_width = windll.user32.GetSystemMetrics(0)
        desktop_height = windll.user32.GetSystemMetrics(1)

        self.geometry(f"{desktop_width}x{desktop_height}+0+0")

        self.gif_path = gif_path
        self.gif_frames = self.load_gif_frames(self.gif_path)
        self.current_frame = 0
        self.click_time = None
        self.click_timer_id = None
        self.dialog = None  # 用于存储对话框的引用
        self.dialog_allowed = True  # 标志，表示是否允许弹窗

        self.create_widgets()

    def create_widgets(self):
        # 创建Canvas用于显示芝麻糕和交互
        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg="white", highlightthickness=0)
        self.canvas.pack()

        # 初始化芝麻糕的位置
        pet_x = self.winfo_screenwidth() // 2
        pet_y = self.winfo_screenheight() // 2
        self.pet_id = self.canvas.create_image(pet_x, pet_y, anchor=tk.CENTER, image=self.gif_frames[0])

        # 绑定事件处理函数
        self.canvas.tag_bind(self.pet_id, '<Button-1>', self.on_pet_click)
        self.canvas.tag_bind(self.pet_id, '<B1-Motion>', self.on_drag)

        # 设置定时器，定时弹出对话框
        self.after(15000, self.schedule_random_dialog)  # Initial delay 15 seconds
        self.after(100, self.update_animation)

        # 创建按钮窗口
        self.button_window = tk.Toplevel(self)
        self.button_window.overrideredirect(True)
        button_window_x = pet_x - 100  # 调整偏移量
        button_window_y = pet_y + 140  # 调整偏移量
        self.button_window.geometry(f"+{int(button_window_x)}+{int(button_window_y)}")  # 设置按钮窗口的位置
        self.button_window.attributes("-topmost", True)  # 保持在最前面

        # 添加按钮
        exit_button = tk.Button(self.button_window, text="退出", command=self.quit)
        exit_button.pack(side=tk.LEFT, padx=10)
        
        pet_button = tk.Button(self.button_window, text="抚摸", command=self.pet_pat)
        pet_button.pack(side=tk.LEFT, padx=10)

        talk_button = tk.Button(self.button_window, text="你想知道什么？", command=self.talk_pat)
        talk_button.pack(side=tk.LEFT, padx=10)

        # 创建对话框
        self.dialog = tk.Toplevel(self)
        self.dialog.title("对话框")
        self.dialog.withdraw()  # 隐藏对话框
        self.dialog_label = tk.Label(self.dialog, padx=10, pady=10)
        self.dialog_label.pack()

        # 绑定鼠标移动事件，实时更新按钮窗口位置
        self.canvas.bind('<B1-Motion>', self.update_button_window_position)

    def load_gif_frames(self, path):
        # 从GIF文件加载帧
        gif = Image.open(path)
        gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
        return gif_frames

    def update_animation(self):
        try:
            # 更新芝麻糕的动画帧
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.canvas.itemconfig(self.pet_id, image=self.gif_frames[self.current_frame])
            self.after(30, self.update_animation)
        except tk.TclError:
            pass

    def on_pet_click(self, event):
        if self.click_timer_id is not None:
            self.after_cancel(self.click_timer_id)

        current_time = self.after(0)
        self.click_time = current_time

        self.show_dialog_wrapper()

        # 不再重新设置随机对话框的触发器

    def on_drag(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.pet_id, x, y)

        # 如果对话框可见，更新对话框的位置
        if self.dialog.winfo_ismapped():
            dialog_x = x + 140  # 调整偏移量
            dialog_y = y - 140  # 调整偏移量
            self.dialog.geometry(f"+{int(dialog_x)}+{int(dialog_y)}")

    def update_button_window_position(self, event):
        x, y = event.x, event.y

        # 更新与用户互动窗口的位置
        button_window_x = x - 100  # 调整偏移量
        button_window_y = y + 140  # 调整偏移量
        self.button_window.geometry(f"+{int(button_window_x)}+{int(button_window_y)}")

    def schedule_random_dialog(self):
        # 每15秒随机弹出对话框，确保只有一个对话框存在
        if self.dialog_allowed:
            if self.dialog:
                self.dialog.withdraw()  # 隐藏对话框

            random_message = random.choice(["邀诸位共赏", "人有五名，代价有三个", "我记得你，小姑娘"])
            self.show_dialog(random_message, duration=2000)

        self.after(15000, self.schedule_random_dialog)  # Reset timer for 15 seconds

    def show_dialog_wrapper(self):
        self.show_dialog("嗯？", duration=3000)

    def show_dialog(self, custom_text=None, duration=5000):
        if custom_text:
            message = custom_text
        else:
            messages = ["邀诸位共赏", "人有五名，代价有三个", "我记得你，小姑娘"]
            message = random.choice(messages)

        # 获取芝麻糕的当前位置
        pet_x, pet_y = self.canvas.coords(self.pet_id)

        # 设置对话框的位置在芝麻糕的右上方
        dialog_x = pet_x + 140  # 调整偏移量
        dialog_y = pet_y - 140  # 调整偏移量
        self.dialog.geometry(f"+{int(dialog_x)}+{int(dialog_y)}")
        self.dialog_label.config(text=message)
        self.dialog.deiconify()  # 显示对话框
        self.dialog_allowed = False  # 不允许在定时器触发之前再次弹窗
        self.after(duration, self.reset_dialog_flag)

    def reset_dialog_flag(self):
        if self.dialog and self.dialog.winfo_exists():
            # 等待一段时间，确保 Tkinter 事件队列中的事件已经完成
            self.after(100, self.hide_dialog)
        else:
            # 如果对话框不存在，直接重置标志
            self.dialog_allowed = True

    def hide_dialog(self):
        # 隐藏对话框
        self.dialog.withdraw()

        # 重置标志
        self.dialog_allowed = True

    def pet_pat(self):
        # 你可以在这里添加抚摸的逻辑，例如播放抚摸的动画或者显示抚摸的消息
        pass

    def talk_pat(self):
        # 暂时还没想好
        pass

if __name__ == "__main__":
    pet_app = DesktopPet("C:/Users/Lenovo/Desktop/blade_desktop_pet/blade.gif")
    pet_app.mainloop()
