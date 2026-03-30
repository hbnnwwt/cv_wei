# -*- coding: utf-8 -*-
"""
Week 01 图像质量检测 - GUI版本
==============================
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def imread_chinese(filepath):
    try:
        img_array = np.fromfile(filepath, dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except:
        return None


class QualityDetectionGUI(ctk.CTk):
    """图像质量检测GUI"""

    def __init__(self):
        super().__init__()
        self.title("Image Quality Detection")
        self.geometry("1200x800")

        # 当前图像
        self.current_image = None
        self.current_gray = None
        self.create_test_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()

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

    def create_test_image(self):
        """创建测试图像"""
        self.current_image = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)

    def setup_ui(self):
        # 顶部框架
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        ctk.CTkLabel(top_frame, text="图像质量检测", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧控制
        self.control_frame = ctk.CTkFrame(self.main_frame, width=280)
        self.control_frame.pack(side="left", fill="y", padx=(0, 10))

        # 右侧显示
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.setup_control()
        self.setup_image_panel()

    def setup_control(self):
        ctk.CTkLabel(self.control_frame, text="操作", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        ctk.CTkButton(self.control_frame, text="打开图像", command=self.open_image).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="生成随机测试图", command=self.generate_random).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="生成模糊图像", command=self.generate_blurry).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="生成过暗图像", command=self.generate_dark).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="生成过亮图像", command=self.generate_bright).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="生成噪声图像", command=self.generate_noisy).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.control_frame, text="开始检测", command=self.detect_quality, fg_color="green").pack(pady=20, fill="x", padx=20)

        # 结果显示
        ctk.CTkLabel(self.control_frame, text="检测结果", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 10))
        self.result_text = ctk.CTkTextbox(self.control_frame, height=200)
        self.result_text.pack(fill="both", padx=20, pady=10, expand=True)

    def setup_image_panel(self):
        self.figure = plt.figure(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.show_image(self.current_image)

    def show_image(self, img):
        plt.clf()
        if len(img.shape) == 2:
            plt.imshow(img, cmap='gray')
        else:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.tight_layout()
        self.canvas.draw()

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("图像", "*.jpg *.png *.bmp")])
        if path:
            img = imread_chinese(path)
            if img is not None:
                self.current_image = img
                self.current_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.show_image(img)
                messagebox.showinfo("成功", "图像已加载")

    def generate_random(self):
        self.current_image = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.show_image(self.current_image)

    def generate_blurry(self):
        self.current_image = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.current_gray = cv2.GaussianBlur(self.current_gray, (15, 15), 0)
        self.current_image = cv2.cvtColor(self.current_gray, cv2.COLOR_GRAY2BGR)
        self.show_image(self.current_image)

    def generate_dark(self):
        self.current_image = np.random.randint(0, 80, (480, 640, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.show_image(self.current_image)

    def generate_bright(self):
        self.current_image = np.random.randint(180, 255, (480, 640, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.show_image(self.current_image)

    def generate_noisy(self):
        self.current_image = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)
        noise = np.random.randint(-50, 50, (480, 640, 3), dtype=np.int16)
        self.current_image = np.clip(self.current_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        self.show_image(self.current_image)

    def detect_quality(self):
        if self.current_gray is None:
            messagebox.showwarning("警告", "请先加载图像")
            return

        # 亮度检测
        brightness = np.mean(self.current_gray)
        if brightness < 80:
            b_status = "过暗"
        elif brightness > 180:
            b_status = "过亮"
        else:
            b_status = "正常"

        # 对比度检测
        contrast = np.std(self.current_gray)
        if contrast < 30:
            c_status = "低对比度"
        elif contrast > 80:
            c_status = "高对比度"
        else:
            c_status = "正常"

        # 清晰度检测
        laplacian = cv2.Laplacian(self.current_gray, cv2.CV_64F)
        blur = laplacian.var()
        if blur < 100:
            bl_status = "模糊"
        elif blur < 500:
            bl_status = "可接受"
        else:
            bl_status = "清晰"

        # 噪声检测
        blurred = cv2.blur(self.current_gray, (5, 5))
        noise = np.abs(self.current_gray.astype(float) - blurred.astype(float))
        noise_ratio = np.mean(noise) / 255.0
        if noise_ratio < 0.02:
            n_status = "干净"
        elif noise_ratio < 0.05:
            n_status = "有噪声"
        else:
            n_status = "噪声严重"

        # 显示结果
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", f"=== 图像质量检测报告 ===\n\n")
        self.result_text.insert("end", f"亮度: {brightness:.1f} ({b_status})\n")
        self.result_text.insert("end", f"对比度: {contrast:.1f} ({c_status})\n")
        self.result_text.insert("end", f"清晰度: {blur:.1f} ({bl_status})\n")
        self.result_text.insert("end", f"噪声: {noise_ratio:.4f} ({n_status})\n")

        # 总体评价
        issues = []
        if b_status != "正常":
            issues.append(b_status)
        if c_status == "低对比度":
            issues.append("低对比度")
        if bl_status == "模糊":
            issues.append("图像模糊")
        if n_status == "噪声严重":
            issues.append("噪声严重")

        if issues:
            self.result_text.insert("end", f"\n⚠️ 问题: {', '.join(issues)}")
        else:
            self.result_text.insert("end", f"\n✅ 图像质量良好")


def main():
    app = QualityDetectionGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
