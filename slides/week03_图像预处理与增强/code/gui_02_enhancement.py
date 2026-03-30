# -*- coding: utf-8 -*-
"""
Week 03 图像增强演示 - GUI版本
=============================
使用 customtkinter 构建的图形界面
展示各种图像增强算法的效果

依赖安装:
    pip install customtkinter opencv-python numpy matplotlib

运行:
    python gui_02_enhancement.py
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


class EnhancementGUI(ctk.CTk):
    """图像增强演示GUI"""

    def __init__(self):
        super().__init__()

        self.title("Week 03 图像增强演示")
        self.geometry("1200x800")

        # 当前图像
        self.original_image = None
        self.gray_image = None
        self.processed_image = None
        self.processed_color = None

        # 加载默认图像
        self.load_default_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.apply_enhancement()

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
            # 创建默认测试图像
            self.original_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

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
            text="图像增强演示 - Week 03",
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

        # 增强方法选择
        ctk.CTkLabel(self.control_frame, text="增强方法", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.method_var = ctk.StringVar(value="clahe")
        methods = [
            ("CLAHE (对比度受限自适应)", "clahe"),
            ("直方图均衡化", "histeq"),
            ("Gamma校正", "gamma"),
            ("线性增强", "linear"),
        ]

        for text, value in methods:
            ctk.CTkRadioButton(
                self.control_frame,
                text=text,
                variable=self.method_var,
                value=value,
                command=self.apply_enhancement
            ).pack(anchor="w", padx=20, pady=2)

        # CLAHE参数
        ctk.CTkLabel(self.control_frame, text="CLAHE Clip Limit", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))

        self.clip_limit = ctk.DoubleVar(value=2.0)
        slider_clip = ctk.CTkSlider(
            self.control_frame,
            from_=1.0,
            to=10.0,
            number_of_steps=18,
            variable=self.clip_limit,
            command=self.apply_enhancement
        )
        slider_clip.pack(fill="x", padx=20)
        self.clip_label = ctk.CTkLabel(self.control_frame, text="2.0")
        self.clip_label.pack()

        ctk.CTkLabel(self.control_frame, text="CLAHE 网格大小", font=ctk.CTkFont(size=14)).pack(pady=(15, 5))

        self.tile_size = ctk.IntVar(value=8)
        slider_tile = ctk.CTkSlider(
            self.control_frame,
            from_=2,
            to=16,
            number_of_steps=7,
            variable=self.tile_size,
            command=self.apply_enhancement
        )
        slider_tile.pack(fill="x", padx=20)
        self.tile_label = ctk.CTkLabel(self.control_frame, text="8")
        self.tile_label.pack()

        # Gamma参数
        ctk.CTkLabel(self.control_frame, text="Gamma 值", font=ctk.CTkFont(size=14)).pack(pady=(15, 5))

        self.gamma = ctk.DoubleVar(value=1.0)
        slider_gamma = ctk.CTkSlider(
            self.control_frame,
            from_=0.1,
            to=3.0,
            number_of_steps=29,
            variable=self.gamma,
            command=self.apply_enhancement
        )
        slider_gamma.pack(fill="x", padx=20)
        self.gamma_label = ctk.CTkLabel(self.control_frame, text="1.0")
        self.gamma_label.pack()

        # 显示模式
        ctk.CTkLabel(self.control_frame, text="显示模式", font=ctk.CTkFont(size=14)).pack(pady=(15, 5))
        self.display_mode = ctk.StringVar(value="gray")
        ctk.CTkRadioButton(self.control_frame, text="灰度图", variable=self.display_mode, value="gray", command=self.update_display).pack(anchor="w", padx=20)
        ctk.CTkRadioButton(self.control_frame, text="彩色图", variable=self.display_mode, value="color", command=self.update_display).pack(anchor="w", padx=20)

    def setup_image_panel(self):
        """设置图像显示面板"""
        # 创建图像画布
        self.figure = plt.figure(figsize=(12, 5), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_display()

    def apply_enhancement(self):
        """应用图像增强"""
        if self.gray_image is None:
            return

        method = self.method_var.get()

        # 更新参数标签
        self.clip_label.configure(text=str(self.clip_limit.get()))
        self.tile_label.configure(text=str(self.tile_size.get()))
        self.gamma_label.configure(text=str(self.gamma.get()))

        if method == "clahe":
            clip = self.clip_limit.get()
            tile = self.tile_size.get()
            clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
            self.processed_image = clahe.apply(self.gray_image)

        elif method == "histeq":
            self.processed_image = cv2.equalizeHist(self.gray_image)

        elif method == "gamma":
            gamma = self.gamma.get()
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
            self.processed_image = cv2.LUT(self.gray_image, table)

        elif method == "linear":
            # 线性增强：调整亮度和对比度
            self.processed_image = cv2.convertScaleAbs(self.gray_image, alpha=1.5, beta=10)

        # 同时处理彩色图
        if self.original_image is not None:
            method = self.method_var.get()
            if method == "clahe":
                clip = self.clip_limit.get()
                tile = self.tile_size.get()
                clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
                lab = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                l = clahe.apply(l)
                self.processed_color = cv2.merge([l, a, b])
                self.processed_color = cv2.cvtColor(self.processed_color, cv2.COLOR_LAB2BGR)
            elif method == "gamma":
                gamma = self.gamma.get()
                inv_gamma = 1.0 / gamma
                table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
                self.processed_color = cv2.LUT(self.original_image, table)
            elif method == "linear":
                self.processed_color = cv2.convertScaleAbs(self.original_image, alpha=1.5, beta=10)
            elif method == "histeq":
                # 直方图均衡化只应用于灰度
                self.processed_color = self.original_image

        self.update_display()

    def update_display(self):
        """更新图像显示"""
        plt.clf()

        mode = self.display_mode.get()

        if mode == "color" and self.original_image is not None:
            # 彩色模式
            plt.subplot(121)
            plt.imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
            plt.title('原图 (彩色)', fontsize=11)
            plt.axis('off')

            plt.subplot(122)
            if self.processed_color is not None:
                plt.imshow(cv2.cvtColor(self.processed_color, cv2.COLOR_BGR2RGB))
                plt.title('增强结果', fontsize=11)
            plt.axis('off')
        else:
            # 灰度模式
            plt.subplot(121)
            if self.gray_image is not None:
                plt.imshow(self.gray_image, cmap='gray')
                plt.title('原图 (灰度)', fontsize=11)
            plt.axis('off')

            plt.subplot(122)
            if self.processed_image is not None:
                plt.imshow(self.processed_image, cmap='gray')
                plt.title('增强结果', fontsize=11)
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
                self.apply_enhancement()
                messagebox.showinfo("成功", f"已加载图像: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")


def main():
    """主函数"""
    app = EnhancementGUI()
    app.mainloop()


if __name__ == "__main__":
    main()