# -*- coding: utf-8 -*-
"""
Week 03 二值化演示 - GUI版本
===========================
使用 customtkinter 构建的图形界面
展示各种二值化算法的效果

依赖安装:
    pip install customtkinter opencv-python numpy matplotlib

运行:
    python gui_03_binarization.py
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


class BinarizationGUI(ctk.CTk):
    """二值化演示GUI"""

    def __init__(self):
        super().__init__()

        self.title("Week 03 二值化演示")
        self.geometry("1200x800")

        # 当前图像
        self.original_image = None
        self.gray_image = None
        self.processed_image = None

        # 加载默认图像
        self.load_default_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.apply_binarization()

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
        """加载默认图像"""
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        default_path = os.path.join(image_dir, 'lena.jpg')

        if os.path.exists(default_path):
            self.original_image = imread_chinese(default_path)
        else:
            # 创建默认测试图像（带渐变和特征）
            test = np.zeros((512, 512), dtype=np.uint8)
            for i in range(512):
                test[i, :] = int(i * 255 / 512)
            # 添加一些特征
            cv2.rectangle(test, (100, 100), (200, 400), 180, -1)
            cv2.circle(test, (350, 256), 50, 80, -1)
            self.original_image = cv2.cvtColor(test, cv2.COLOR_GRAY2BGR)

        # 转换为灰度图
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

    def setup_ui(self):
        """设置界面"""
        # 顶部框架
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        ctk.CTkLabel(
            top_frame,
            text="图像二值化演示 - Week 03",
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

        # 阈值方法选择
        ctk.CTkLabel(self.control_frame, text="阈值方法", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.method_var = ctk.StringVar(value="otsu")
        methods = [
            ("固定阈值", "fixed"),
            ("Otsu最优阈值", "otsu"),
            ("自适应均值", "adaptive_mean"),
            ("自适应高斯", "adaptive_gaussian"),
        ]

        for text, value in methods:
            ctk.CTkRadioButton(
                self.control_frame,
                text=text,
                variable=self.method_var,
                value=value,
                command=self.apply_binarization
            ).pack(anchor="w", padx=20, pady=2)

        # 固定阈值参数
        ctk.CTkLabel(self.control_frame, text="固定阈值 (0-255)", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.threshold_value = ctk.IntVar(value=127)
        slider = ctk.CTkSlider(
            self.control_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            variable=self.threshold_value,
            command=self.on_threshold_change
        )
        slider.pack(fill="x", padx=20)
        self.threshold_label = ctk.CTkLabel(self.control_frame, text="127")
        self.threshold_label.pack()

        # 自适应参数
        ctk.CTkLabel(self.control_frame, text="自适应块大小 (奇数)", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.block_size = ctk.IntVar(value=11)
        slider_block = ctk.CTkSlider(
            self.control_frame,
            from_=3,
            to=31,
            number_of_steps=14,
            variable=self.block_size,
            command=self.on_block_change
        )
        slider_block.pack(fill="x", padx=20)
        self.block_label = ctk.CTkLabel(self.control_frame, text="11")
        self.block_label.pack()

        ctk.CTkLabel(self.control_frame, text="C 常数 (减去的值)", font=ctk.CTkFont(size=14)).pack(pady=(15, 5))

        self.c_constant = ctk.IntVar(value=2)
        slider_c = ctk.CTkSlider(
            self.control_frame,
            from_=-20,
            to=20,
            number_of_steps=40,
            variable=self.c_constant,
            command=self.apply_binarization
        )
        slider_c.pack(fill="x", padx=20)
        self.c_label = ctk.CTkLabel(self.control_frame, text="2")
        self.c_label.pack()

    def on_threshold_change(self, value):
        """阈值变化回调"""
        self.threshold_label.configure(text=str(int(value)))
        if self.method_var.get() == "fixed":
            self.apply_binarization()

    def on_block_change(self, value):
        """块大小变化回调"""
        # 确保为奇数
        b = int(value)
        if b % 2 == 0:
            b += 1
        self.block_size.set(b)
        self.block_label.configure(text=str(b))
        if self.method_var.get() != "fixed":
            self.apply_binarization()

    def setup_image_panel(self):
        """设置图像显示面板"""
        # 创建图像画布
        self.figure = plt.figure(figsize=(12, 5), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_display()

    def apply_binarization(self):
        """应用二值化"""
        if self.gray_image is None:
            return

        method = self.method_var.get()

        # 更新参数标签
        self.threshold_label.configure(text=str(self.threshold_value.get()))
        self.block_label.configure(text=str(self.block_size.get()))
        self.c_label.configure(text=str(self.c_constant.get()))

        # 获取参数
        thresh_val = self.threshold_value.get()
        block_size = self.block_size.get()
        if block_size % 2 == 0:
            block_size += 1
        c_val = self.c_constant.get()

        if method == "fixed":
            _, self.processed_image = cv2.threshold(self.gray_image, thresh_val, 255, cv2.THRESH_BINARY)

        elif method == "otsu":
            # Otsu自动计算最优阈值
            _, self.processed_image = cv2.threshold(
                self.gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            # 显示计算出的阈值
            self.threshold_label.configure(text=f"自动: {_}")

        elif method == "adaptive_mean":
            self.processed_image = cv2.adaptiveThreshold(
                self.gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, block_size, c_val
            )

        elif method == "adaptive_gaussian":
            self.processed_image = cv2.adaptiveThreshold(
                self.gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, block_size, c_val
            )

        self.update_display()

    def update_display(self):
        """更新图像显示"""
        plt.clf()

        # 显示三张图：原图、直方图、二值化结果
        plt.subplot(131)
        if self.gray_image is not None:
            plt.imshow(self.gray_image, cmap='gray')
        plt.title('原图 (灰度)', fontsize=11)
        plt.axis('off')

        plt.subplot(132)
        if self.gray_image is not None:
            plt.hist(self.gray_image.flatten(), bins=50, color='steelblue', alpha=0.7)
            plt.axvline(x=127, color='red', linestyle='--', label='阈值')
            plt.legend()
        plt.title('灰度直方图', fontsize=11)
        plt.xlabel('灰度值')
        plt.ylabel('像素数')

        plt.subplot(133)
        if self.processed_image is not None:
            plt.imshow(self.processed_image, cmap='gray')
            plt.title('二值化结果', fontsize=11)
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
                self.gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.apply_binarization()
                messagebox.showinfo("成功", f"已加载图像: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")


def main():
    """主函数"""
    app = BinarizationGUI()
    app.mainloop()


if __name__ == "__main__":
    main()