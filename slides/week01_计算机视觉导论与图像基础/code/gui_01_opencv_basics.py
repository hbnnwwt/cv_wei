# -*- coding: utf-8 -*-
"""
Week 01 OpenCV 基础演示 - GUI版本
===============================
使用 customtkinter 构建的图形界面

依赖安装:
    pip install customtkinter opencv-python numpy matplotlib

运行:
    python gui_opencv_basics.py
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


class OpenCVBasicsGUI(ctk.CTk):
    """OpenCV基础演示GUI"""

    def __init__(self):
        super().__init__()

        self.title("OpenCV Basics Demo - Week 01")
        self.geometry("1200x800")

        # 当前图像
        self.current_image = None
        self.current_gray = None

        # 加载默认图像
        self.load_default_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()

    def update_all_gui_theme(self, mode):
        """更新所有GUI的主题设置（现在从配置文件读取，此方法保留兼容）"""
        # 主题已改为从配置文件读取，无需修改文件
        pass

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
            self.current_image = imread_chinese(default_path)
            if self.current_image is not None:
                self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
                return

        # 如果没有图片，创建一个测试图像
        self.current_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        self.current_gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)

    def setup_ui(self):
        """设置界面"""
        # 顶部框架
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        self.title_label = ctk.CTkLabel(
            top_frame,
            text="OpenCV 基础演示 - Week 01",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")

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
        ctk.CTkButton(self.control_frame, text="保存图像", command=self.save_image).pack(fill="x", padx=20, pady=5)

        # 基础操作
        ctk.CTkLabel(self.control_frame, text="图像基础操作", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.ops = {
            "原图显示": lambda: self.show_image(self.current_image),
            "灰度转换": lambda: self.show_image(self.current_gray, gray=True),
            "RGB转换": lambda: self.show_image(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)),
            "垂直翻转": lambda: self.show_image(cv2.flip(self.current_image, 0)),
            "水平翻转": lambda: self.show_image(cv2.flip(self.current_image, 1)),
            "裁剪中心": lambda: self.crop_center(),
        }

        for op_name, op_func in self.ops.items():
            ctk.CTkButton(self.control_frame, text=op_name, command=op_func).pack(fill="x", padx=20, pady=3)

        # 滤镜操作
        ctk.CTkLabel(self.control_frame, text="图像滤镜", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.filters = {
            "均值模糊": lambda: self.apply_filter("blur"),
            "高斯模糊": lambda: self.apply_filter("gaussian"),
            "中值滤波": lambda: self.apply_filter("median"),
            "边缘检测": lambda: self.apply_filter("canny"),
            "锐化": lambda: self.apply_filter("sharpen"),
        }

        for filter_name, filter_func in self.filters.items():
            ctk.CTkButton(self.control_frame, text=filter_name, command=filter_func).pack(fill="x", padx=20, pady=3)

        # 图像增强
        ctk.CTkLabel(self.control_frame, text="图像增强", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.enhance = {
            "直方图均衡化": lambda: self.apply_enhance("equalize"),
            "亮度增加": lambda: self.apply_enhance("bright"),
            "对比度增加": lambda: self.apply_enhance("contrast"),
        }

        for name, func in self.enhance.items():
            ctk.CTkButton(self.control_frame, text=name, command=func).pack(fill="x", padx=20, pady=3)

    def setup_image_panel(self):
        """设置图像显示面板"""
        # 图像画布
        self.figure = plt.figure(figsize=(8, 6), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # 显示默认图像
        self.show_image(self.current_image)

    def show_image(self, img, gray=False):
        """显示图像"""
        plt.clf()

        if gray or len(img.shape) == 2:
            plt.imshow(img, cmap='gray')
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img.shape[2] == 3 else img
            plt.imshow(img_rgb)

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
                self.current_image = img
                self.current_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.show_image(img)
                messagebox.showinfo("成功", f"已加载图像: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")

    def save_image(self):
        """保存图像"""
        if self.current_image is None:
            messagebox.showwarning("警告", "没有可保存的图像")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存图像",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        )

        if file_path:
            # 使用 cv2.imencode 保存中文路径
            ext = os.path.splitext(file_path)[1]
            ext = ext.lower().replace('.', '')
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            if ext == 'png':
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 9]

            _, buf = cv2.imencode(ext, self.current_image, encode_param)
            buf.tofile(file_path)
            messagebox.showinfo("成功", f"图像已保存到: {os.path.basename(file_path)}")

    def crop_center(self):
        """裁剪中心区域"""
        if self.current_image is None:
            return

        h, w = self.current_image.shape[:2]
        crop = self.current_image[h//4:3*h//4, w//4:3*w//4]
        self.show_image(crop)

    def apply_filter(self, filter_type):
        """应用滤镜"""
        if self.current_gray is None:
            return

        if filter_type == "blur":
            result = cv2.blur(self.current_gray, (5, 5))
        elif filter_type == "gaussian":
            result = cv2.GaussianBlur(self.current_gray, (5, 5), 0)
        elif filter_type == "median":
            result = cv2.medianBlur(self.current_gray, 5)
        elif filter_type == "canny":
            result = cv2.Canny(self.current_gray, 50, 150)
        elif filter_type == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            result = cv2.filter2D(self.current_gray, -1, kernel)
        else:
            return

        self.show_image(result, gray=True)

    def apply_enhance(self, enhance_type):
        """应用图像增强"""
        if self.current_gray is None:
            return

        if enhance_type == "equalize":
            result = cv2.equalizeHist(self.current_gray)
        elif enhance_type == "bright":
            result = cv2.convertScaleAbs(self.current_gray, alpha=1.2, beta=30)
        elif enhance_type == "contrast":
            result = cv2.convertScaleAbs(self.current_gray, alpha=1.5, beta=0)
        else:
            return

        self.show_image(result, gray=True)


def main():
    """主函数"""
    app = OpenCVBasicsGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
