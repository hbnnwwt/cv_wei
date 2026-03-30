# -*- coding: utf-8 -*-
"""
Week 03 去噪演示 - GUI版本
==========================
使用 customtkinter 构建的图形界面
展示各种滤波器的去噪效果

依赖安装:
    pip install customtkinter opencv-python numpy matplotlib

运行:
    python gui_01_denoising.py
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

# 配置 matplotlib 中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置主题（从配置文件读取）
from gui_config import get_appearance_mode
current_mode = get_appearance_mode()
ctk.set_appearance_mode(current_mode)
ctk.set_default_color_theme("blue")

# 导入工具函数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def imread_chinese(filepath):
    """读取中文路径图片"""
    try:
        img_array = np.fromfile(filepath, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


class DenoisingGUI(ctk.CTk):
    """去噪演示GUI"""

    def __init__(self):
        super().__init__()

        self.title("Week 03 去噪演示")
        self.geometry("1200x800")

        # 当前图像
        self.original_image = None
        self.noisy_image = None
        self.processed_image = None

        # 加载默认图像
        self.load_default_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.apply_denoising()

    def on_closing(self):
        """窗口关闭时的清理"""
        try:
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'figure'):
                plt.close(self.figure)
        except:
            pass
        self.destroy()

    def load_default_image(self):
        """加载默认图像（添加噪声）"""
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        default_path = os.path.join(image_dir, 'lena.jpg')

        if os.path.exists(default_path):
            self.original_image = imread_chinese(default_path)
        else:
            # 创建默认测试图像
            self.original_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

        # 创建噪声图像
        self.noisy_image = self.add_noise(self.original_image)

    def add_noise(self, img):
        """添加高斯噪声和椒盐噪声"""
        noisy = img.copy().astype(np.float64)

        # 添加高斯噪声
        noise = np.random.normal(0, 25, img.shape)
        noisy = noisy + noise

        # 添加少量椒盐噪声
        salt_pepper = np.random.random(img.shape)
        noisy[salt_pepper < 0.02] = 0
        noisy[salt_pepper > 0.98] = 255

        return np.clip(noisy, 0, 255).astype(np.uint8)

    def setup_ui(self):
        """设置界面"""
        # 顶部框架
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        ctk.CTkLabel(
            top_frame,
            text="图像去噪演示 - Week 03",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        # 主框架（左右分栏）
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧控制面板
        self.control_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.control_frame.pack(side="left", fill="y", padx=(0, 10))

        # 右侧图像显示
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.setup_control_panel()
        self.setup_image_panel()

    def setup_control_panel(self):
        """设置控制面板"""
        # 文件操作
        ctk.CTkLabel(self.control_frame, text="文件操作", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ctk.CTkButton(self.control_frame, text="打开图像", command=self.open_image).pack(fill="x", padx=20, pady=5)

        # 滤波器选择
        ctk.CTkLabel(self.control_frame, text="滤波器类型", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.filter_var = ctk.StringVar(value="mean")
        filters = [
            ("均值滤波 (Mean)", "mean"),
            ("高斯滤波 (Gaussian)", "gaussian"),
            ("中值滤波 (Median)", "median"),
            ("双边滤波 (Bilateral)", "bilateral"),
        ]

        for text, value in filters:
            ctk.CTkRadioButton(
                self.control_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                command=self.apply_denoising
            ).pack(anchor="w", padx=20, pady=2)

        # 核大小滑块
        ctk.CTkLabel(self.control_frame, text="核大小 (Kernal Size)", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.kernel_size = ctk.IntVar(value=5)
        slider = ctk.CTkSlider(
            self.control_frame,
            from_=3,
            to=15,
            number_of_steps=6,
            variable=self.kernel_size,
            command=self.on_kernel_change
        )
        slider.pack(fill="x", padx=20)

        self.kernel_label = ctk.CTkLabel(self.control_frame, text="5")
        self.kernel_label.pack()

        # 双边滤波专用参数
        self.sigma_color_label = ctk.CTkLabel(self.control_frame, text="Sigma Color", font=ctk.CTkFont(size=14))
        self.sigma_color_label.pack(pady=(15, 5))
        self.sigma_color = ctk.IntVar(value=50)
        slider_color = ctk.CTkSlider(
            self.control_frame,
            from_=10,
            to=150,
            number_of_steps=14,
            variable=self.sigma_color,
            command=self.apply_denoising
        )
        slider_color.pack(fill="x", padx=20)
        self.sigma_color_value = ctk.CTkLabel(self.control_frame, text="50")
        self.sigma_color_value.pack()

        # 重置按钮
        ctk.CTkButton(
            self.control_frame,
            text="重置为噪声图像",
            command=self.reset_to_noisy,
            fg_color="orange"
        ).pack(pady=20, padx=20)

    def on_kernel_change(self, value):
        """核大小变化回调"""
        # 确保为奇数
        k = int(value)
        if k % 2 == 0:
            k += 1
        self.kernel_size.set(k)
        self.kernel_label.configure(text=str(k))
        self.apply_denoising()

    def setup_image_panel(self):
        """设置图像显示面板"""
        # 创建图像画布（显示原图、噪声图、处理后）
        self.figure = plt.figure(figsize=(12, 5), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_display()

    def apply_denoising(self):
        """应用去噪处理"""
        if self.noisy_image is None:
            return

        k = self.kernel_size.get()
        if k % 2 == 0:
            k += 1

        filter_type = self.filter_var.get()
        gray = cv2.cvtColor(self.noisy_image, cv2.COLOR_BGR2GRAY)

        if filter_type == "mean":
            self.processed_image = cv2.blur(gray, (k, k))
        elif filter_type == "gaussian":
            self.processed_image = cv2.GaussianBlur(gray, (k, k), 0)
        elif filter_type == "median":
            self.processed_image = cv2.medianBlur(gray, k)
        elif filter_type == "bilateral":
            sigma = self.sigma_color.get()
            self.processed_image = cv2.bilateralFilter(gray, k, sigma, sigma)

        self.update_display()

    def update_display(self):
        """更新图像显示"""
        plt.clf()

        # 显示三张图
        plt.subplot(131)
        if self.original_image is not None:
            plt.imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        plt.title('原图', fontsize=11)
        plt.axis('off')

        plt.subplot(132)
        if self.noisy_image is not None:
            plt.imshow(cv2.cvtColor(self.noisy_image, cv2.COLOR_BGR2RGB))
        plt.title('加噪声', fontsize=11)
        plt.axis('off')

        plt.subplot(133)
        if self.processed_image is not None:
            plt.imshow(self.processed_image, cmap='gray')
            plt.title('去噪结果', fontsize=11)
        plt.axis('off')

        plt.tight_layout()
        self.canvas.draw()

    def open_image(self):
        """打开图像文件"""
        file_path = filedialog.askopenfilename(
            title="选择图像文件",
            filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )

        if file_path:
            img = imread_chinese(file_path)
            if img is not None:
                self.original_image = img
                self.noisy_image = self.add_noise(img)
                self.apply_denoising()
                messagebox.showinfo("成功", f"已加载图像: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")

    def reset_to_noisy(self):
        """重置为噪声图像"""
        if self.noisy_image is not None:
            self.processed_image = cv2.cvtColor(self.noisy_image, cv2.COLOR_BGR2GRAY)
            self.update_display()


def main():
    """主函数"""
    app = DenoisingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()