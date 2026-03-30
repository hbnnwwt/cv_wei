# -*- coding: utf-8 -*-
"""
Week 01 阅卷系统预处理 - GUI版本
==============================
带有参数调整功能的交互式演示
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


class GradingSystemGUI(ctk.CTk):
    """阅卷系统预处理GUI - 带有参数调整功能"""

    def __init__(self):
        super().__init__()
        self.title("阅卷系统预处理 - 参数调整演示")
        self.geometry("1200x800")

        # 预处理参数
        self.canny_low = 50
        self.canny_high = 150
        self.kernel_size = 5
        self.morph_iterations = 1
        self.area_threshold = 10000

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
        """创建测试答题卡图像"""
        img = np.ones((600, 800, 3), dtype=np.uint8) * 240

        # 绘制答题卡边框
        cv2.rectangle(img, (100, 50), (700, 550), (0, 0, 0), 3)

        # 绘制内部格子（模拟答题区域）
        for i in range(5):
            y = 100 + i * 80
            cv2.line(img, (150, y), (650, y), (200, 200, 200), 1)

        for i in range(6):
            x = 150 + i * 100
            cv2.line(img, (x, 100), (x, 480), (200, 200, 200), 1)

        # 添加一些噪点
        noise = np.random.randint(-30, 30, img.shape, dtype=np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        return img

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        self.title_label = ctk.CTkLabel(
            top_frame,
            text="阅卷系统预处理 - 参数调整演示",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧控制面板
        self.control_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.control_frame.pack(side="left", fill="y", padx=(0, 10))

        # 右侧图像显示
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.setup_control()
        self.setup_image_panel()

    def setup_control(self):
        """设置控制面板"""
        ctk.CTkLabel(self.control_frame, text="参数设置",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Canny 边缘检测低阈值
        ctk.CTkLabel(self.control_frame, text="边缘检测 - 低阈值:").pack(pady=(10, 0))
        self.canny_low_slider = ctk.CTkSlider(self.control_frame, from_=0, to=200, number_of_steps=40)
        self.canny_low_slider.set(self.canny_low)
        self.canny_low_slider.pack(fill="x", padx=20)
        self.canny_low_label = ctk.CTkLabel(self.control_frame, text=f"{self.canny_low}")
        self.canny_low_label.pack()

        # Canny 边缘检测高阈值
        ctk.CTkLabel(self.control_frame, text="边缘检测 - 高阈值:").pack(pady=(10, 0))
        self.canny_high_slider = ctk.CTkSlider(self.control_frame, from_=0, to=300, number_of_steps=60)
        self.canny_high_slider.set(self.canny_high)
        self.canny_high_slider.pack(fill="x", padx=20)
        self.canny_high_label = ctk.CTkLabel(self.control_frame, text=f"{self.canny_high}")
        self.canny_high_label.pack()

        # 形态学操作 - 卷积核大小
        ctk.CTkLabel(self.control_frame, text="形态学 - 卷积核大小:").pack(pady=(10, 0))
        self.kernel_slider = ctk.CTkSlider(self.control_frame, from_=3, to=15, number_of_steps=12)
        self.kernel_slider.set(self.kernel_size)
        self.kernel_slider.pack(fill="x", padx=20)
        self.kernel_label = ctk.CTkLabel(self.control_frame, text=f"{self.kernel_size}")
        self.kernel_label.pack()

        # 形态学操作 - 迭代次数
        ctk.CTkLabel(self.control_frame, text="形态学 - 迭代次数:").pack(pady=(10, 0))
        self.morph_slider = ctk.CTkSlider(self.control_frame, from_=1, to=5, number_of_steps=4)
        self.morph_slider.set(self.morph_iterations)
        self.morph_slider.pack(fill="x", padx=20)
        self.morph_label = ctk.CTkLabel(self.control_frame, text=f"{self.morph_iterations}")
        self.morph_label.pack()

        # 面积阈值
        ctk.CTkLabel(self.control_frame, text="轮廓面积阈值:").pack(pady=(10, 0))
        self.area_slider = ctk.CTkSlider(self.control_frame, from_=1000, to=50000, number_of_steps=49)
        self.area_slider.set(self.area_threshold)
        self.area_slider.pack(fill="x", padx=20)
        self.area_label = ctk.CTkLabel(self.control_frame, text=f"{self.area_threshold}")
        self.area_label.pack()

        # 应用按钮
        ctk.CTkButton(self.control_frame, text="应用参数",
                     command=self.apply_params).pack(pady=20, fill="x", padx=20)

        # 操作按钮
        ctk.CTkLabel(self.control_frame, text="操作",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        ctk.CTkButton(self.control_frame, text="重新生成测试图像",
                     command=self.regenerate_image).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="显示原图",
                     command=self.show_original).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="显示灰度图",
                     command=self.show_gray).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="显示边缘检测",
                     command=self.show_edges).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="显示形态学结果",
                     command=self.show_morphology).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="显示轮廓结果",
                     command=self.show_contours).pack(fill="x", padx=20, pady=5)

    def setup_image_panel(self):
        self.figure = plt.figure(figsize=(8, 6), facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.show_original()

    def apply_params(self):
        """应用参数"""
        self.canny_low = int(self.canny_low_slider.get())
        self.canny_high = int(self.canny_high_slider.get())
        self.kernel_size = int(self.kernel_slider.get())
        if self.kernel_size % 2 == 0:
            self.kernel_size += 1
        self.morph_iterations = int(self.morph_slider.get())
        self.area_threshold = int(self.area_slider.get())

        self.canny_low_label.configure(text=f"{self.canny_low}")
        self.canny_high_label.configure(text=f"{self.canny_high}")
        self.kernel_label.configure(text=f"{self.kernel_size}")
        self.morph_label.configure(text=f"{self.morph_iterations}")
        self.area_label.configure(text=f"{self.area_threshold}")

        messagebox.showinfo("参数已更新",
            f"边缘检测阈值: {self.canny_low} / {self.canny_high}\n"
            f"卷积核大小: {self.kernel_size}\n"
            f"迭代次数: {self.morph_iterations}\n"
            f"面积阈值: {self.area_threshold}")

        # 自动显示边缘检测结果
        self.show_edges()

    def regenerate_image(self):
        """重新生成测试图像"""
        self.test_image = self.create_test_image()
        self.show_original()
        messagebox.showinfo("完成", "测试图像已重新生成")

    def show_image(self, img, title="Image"):
        plt.clf()
        if len(img.shape) == 2:
            plt.imshow(img, cmap='gray')
        else:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(title, color='black')
        plt.axis('off')
        plt.tight_layout()
        self.canvas.draw()

    def show_original(self):
        """显示原图"""
        self.show_image(self.test_image, "原始图像")

    def show_gray(self):
        """显示灰度图"""
        gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        self.show_image(gray, "灰度化结果")

    def show_edges(self):
        """显示边缘检测结果"""
        gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        self.show_image(edges, f"边缘检测 (阈值: {self.canny_low}/{self.canny_high})")

    def show_morphology(self):
        """显示形态学操作结果"""
        gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel,
                                iterations=self.morph_iterations)
        self.show_image(morph, f"形态学操作 (核:{self.kernel_size}, 迭代:{self.morph_iterations})")

    def show_contours(self):
        """显示轮廓检测结果"""
        gray = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel,
                                iterations=self.morph_iterations)

        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL,
                                      cv2.CHAIN_APPROX_SIMPLE)

        # 绘制结果
        result = self.test_image.copy()
        cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

        # 筛选符合条件的轮廓
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.area_threshold]
        cv2.drawContours(result, valid_contours, -1, (255, 0, 0), 3)

        self.show_image(result, f"轮廓检测 (共{len(contours)}个, 有效{len(valid_contours)}个)")


def main():
    app = GradingSystemGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
