# -*- coding: utf-8 -*-
"""
Week 01 闪电编程挑战 - GUI版本
==============================
交互式编程挑战演示
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

from gui_config import get_appearance_mode
current_mode = get_appearance_mode()
ctk.set_appearance_mode(current_mode)
ctk.set_default_color_theme("blue")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class QuickChallengeGUI(ctk.CTk):
    """闪电编程挑战GUI"""

    def __init__(self):
        super().__init__()
        self.title("闪电编程挑战 - NumPy实战")
        self.geometry("1200x800")

        # 挑战参数
        self.roi_x_start = 270
        self.roi_x_end = 370
        self.roi_y_start = 190
        self.roi_y_end = 290

        # 创建测试图像
        self.test_image = self.create_test_image()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()

    def on_closing(self):
        try:
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'figure'):
                plt.close(self.figure)
        except:
            pass
        self.destroy()

    def create_test_image(self):
        """创建测试图像（含噪声和光照不均）"""
        img = np.random.randint(0, 256, (480, 640), dtype=np.uint8)

        # 添加光照不均效果（模拟左边亮右边暗）
        gradient = np.linspace(50, 150, 640)
        img = img + gradient.astype(np.uint8)

        # 限制范围
        img = np.clip(img, 0, 255)

        return img

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        self.title_label = ctk.CTkLabel(
            top_frame,
            text="闪电编程挑战 - NumPy数组操作",
            font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧挑战说明
        self.challenge_frame = ctk.CTkFrame(self.main_frame, width=400)
        self.challenge_frame.pack(side="left", fill="both", padx=(0, 10))

        # 右侧图像显示
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.setup_challenge_panel()
        self.setup_image_panel()

    def setup_challenge_panel(self):
        """设置挑战说明面板"""
        ctk.CTkLabel(self.challenge_frame, text="挑战题目",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        challenge_text = """
【挑战题目】

给定一张"脏"试卷图像（含噪声，光照不均）

任务：用代码提取出学号区的均值

【场景】
假设学号区域在图像中心 100x100 像素区域

【目标】
让同学们熟悉 NumPy 数组操作
        """
        ctk.CTkLabel(self.challenge_frame, text=challenge_text,
                    justify="left", anchor="w").pack(padx=20, pady=5)

        # ROI 参数调整
        ctk.CTkLabel(self.challenge_frame, text="ROI参数调整",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        # X起始
        ctk.CTkLabel(self.challenge_frame, text="X起始位置:").pack(pady=(5, 0))
        self.x_start_slider = ctk.CTkSlider(self.challenge_frame, from_=0, to=540, number_of_steps=54)
        self.x_start_slider.set(self.roi_x_start)
        self.x_start_slider.pack(fill="x", padx=20)
        self.x_start_label = ctk.CTkLabel(self.challenge_frame, text=f"{self.roi_x_start}")
        self.x_start_label.pack()

        # X结束
        ctk.CTkLabel(self.challenge_frame, text="X结束位置:").pack(pady=(5, 0))
        self.x_end_slider = ctk.CTkSlider(self.challenge_frame, from_=100, to=640, number_of_steps=54)
        self.x_end_slider.set(self.roi_x_end)
        self.x_end_slider.pack(fill="x", padx=20)
        self.x_end_label = ctk.CTkLabel(self.challenge_frame, text=f"{self.roi_x_end}")
        self.x_end_label.pack()

        # Y起始
        ctk.CTkLabel(self.challenge_frame, text="Y起始位置:").pack(pady=(5, 0))
        self.y_start_slider = ctk.CTkSlider(self.challenge_frame, from_=0, to=380, number_of_steps=38)
        self.y_start_slider.set(self.roi_y_start)
        self.y_start_slider.pack(fill="x", padx=20)
        self.y_start_label = ctk.CTkLabel(self.challenge_frame, text=f"{self.roi_y_start}")
        self.y_start_label.pack()

        # Y结束
        ctk.CTkLabel(self.challenge_frame, text="Y结束位置:").pack(pady=(5, 0))
        self.y_end_slider = ctk.CTkSlider(self.challenge_frame, from_=100, to=480, number_of_steps=38)
        self.y_end_slider.set(self.roi_y_end)
        self.y_end_slider.pack(fill="x", padx=20)
        self.y_end_label = ctk.CTkLabel(self.challenge_frame, text=f"{self.roi_y_end}")
        self.y_end_label.pack()

        # 按钮
        ctk.CTkButton(self.challenge_frame, text="运行代码",
                     command=self.run_code).pack(pady=15, fill="x", padx=20)

        ctk.CTkButton(self.challenge_frame, text="显示参考答案",
                     command=self.show_answer).pack(pady=5, fill="x", padx=20)

        # 结果显示
        ctk.CTkLabel(self.challenge_frame, text="运行结果:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        self.result_label = ctk.CTkLabel(self.challenge_frame, text="点击「运行代码」查看结果",
                                         text_color="gray")
        self.result_label.pack(pady=5)

        # 代码预览
        ctk.CTkLabel(self.challenge_frame, text="当前代码:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))

        self.code_text = ctk.CTkTextbox(self.challenge_frame, height=80)
        self.code_text.pack(padx=20, pady=5, fill="x")
        self.code_text.insert("1.0",
            "# 提取ROI区域\nroi = img[y_start:y_end, x_start:x_end]\n\n"
            "# 计算均值\nmean_val = np.mean(roi)")

    def setup_image_panel(self):
        self.figure = plt.figure(figsize=(6, 5), facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.show_image()

    def show_image(self):
        """显示图像和ROI区域"""
        plt.clf()

        # 创建带标记的图像
        display_img = cv2.cvtColor(self.test_image, cv2.COLOR_GRAY2BGR)

        # 绘制ROI区域
        cv2.rectangle(display_img,
                     (self.roi_x_start, self.roi_y_start),
                     (self.roi_x_end, self.roi_y_end),
                     (0, 255, 0), 2)

        # 转换为RGB显示
        display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)

        plt.imshow(display_img)
        plt.title(f"学号区域ROI (X:{self.roi_x_start}-{self.roi_x_end}, Y:{self.roi_y_start}-{self.roi_y_end})",
                 color='black', fontsize=10)
        plt.xlabel("像素位置 X")
        plt.ylabel("像素位置 Y")
        plt.colorbar(label='亮度值')
        plt.tight_layout()
        self.canvas.draw()

    def run_code(self):
        """运行代码并显示结果"""
        # 更新参数
        self.roi_x_start = int(self.x_start_slider.get())
        self.roi_x_end = int(self.x_end_slider.get())
        self.roi_y_start = int(self.y_start_slider.get())
        self.roi_y_end = int(self.y_end_slider.get())

        # 确保范围正确
        if self.roi_x_start >= self.roi_x_end:
            self.roi_x_end = self.roi_x_start + 10
        if self.roi_y_start >= self.roi_y_end:
            self.roi_y_end = self.roi_y_start + 10

        # 更新标签
        self.x_start_label.configure(text=f"{self.roi_x_start}")
        self.x_end_label.configure(text=f"{self.roi_x_end}")
        self.y_start_label.configure(text=f"{self.roi_y_start}")
        self.y_end_label.configure(text=f"{self.roi_y_end}")

        # 提取ROI
        roi = self.test_image[self.roi_y_start:self.roi_y_end,
                             self.roi_x_start:self.roi_x_end]

        if roi.size == 0:
            self.result_label.configure(text="ROI区域无效！")
            return

        # 计算各种统计值
        mean_val = np.mean(roi)
        median_val = np.median(roi)
        std_val = np.std(roi)
        min_val = np.min(roi)
        max_val = np.max(roi)

        # 找最亮和最暗位置
        min_loc = np.argmin(roi)
        max_loc = np.argmax(roi)
        min_row, min_col = min_loc // roi.shape[1], min_loc % roi.shape[1]
        max_row, max_col = max_loc // roi.shape[1], max_loc % roi.shape[1]

        # 显示结果
        result_text = f"""均值: {mean_val:.2f}
中位数: {median_val:.2f}
标准差: {std_val:.2f}
最小值: {min_val} (位置: row={min_row}, col={min_col})
最大值: {max_val} (位置: row={max_row}, col={max_col})"""

        self.result_label.configure(text=result_text)

        # 显示图像
        self.show_image()

        messagebox.showinfo("运行结果", result_text)

    def show_answer(self):
        """显示参考答案"""
        answer_text = """
【参考答案】

# 3行版本
y1, y2 = 190, 290  # Y起始和结束
x1, x2 = 270, 370  # X起始和结束
roi = img[y1:y2, x1:x2]  # 提取ROI
mean_val = np.mean(roi)   # 计算均值

# 1行版本
mean_val = np.mean(img[190:290, 270:370])

# 扩展挑战
row_means = np.mean(roi, axis=1)  # 每行的均值
col_means = np.mean(roi, axis=0)  # 每列的均值

# 找最值位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(roi)
"""
        messagebox.showinfo("参考答案", answer_text)


def main():
    app = QuickChallengeGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
