# -*- coding: utf-8 -*-
"""
Week 03 几何变换演示 - GUI版本
============================
使用 customtkinter 构建的图形界面
展示各种几何变换的效果

依赖安装:
    pip install customtkinter opencv-python numpy matplotlib

运行:
    python gui_04_geometry.py
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


class GeometryGUI(ctk.CTk):
    """几何变换演示GUI"""

    def __init__(self):
        super().__init__()

        self.title("Week 03 几何变换演示")
        self.geometry("1200x800")

        # 当前图像
        self.original_image = None
        self.processed_image = None

        # 加载默认图像
        self.load_default_image()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_ui()
        self.apply_transform()

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
            # 创建默认测试图像（带特征点）
            self.original_image = np.zeros((400, 400, 3), dtype=np.uint8)
            self.original_image[:, :] = (240, 240, 240)
            # 添加网格
            for i in range(0, 400, 40):
                cv2.line(self.original_image, (i, 0), (i, 400), (220, 220, 220), 1)
                cv2.line(self.original_image, (0, i), (400, i), (220, 220, 220), 1)
            # 添加特征点
            cv2.circle(self.original_image, (80, 80), 20, (255, 0, 0), -1)
            cv2.circle(self.original_image, (320, 80), 20, (0, 255, 0), -1)
            cv2.circle(self.original_image, (80, 320), 20, (0, 0, 255), -1)
            cv2.circle(self.original_image, (320, 320), 20, (255, 255, 0), -1)
            # 添加中心文字区域
            cv2.rectangle(self.original_image, (150, 150), (250, 250), (200, 200, 200), -1)
            cv2.putText(self.original_image, "TEST", (170, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    def setup_ui(self):
        """设置界面"""
        # 顶部框架
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        ctk.CTkLabel(
            top_frame,
            text="几何变换演示 - Week 03",
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

        # 变换类型选择
        ctk.CTkLabel(self.control_frame, text="变换类型", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        self.transform_var = ctk.StringVar(value="rotate")
        transforms = [
            ("旋转", "rotate"),
            ("缩放", "scale"),
            ("平移", "translate"),
            ("仿射变换", "affine"),
            ("透视变换", "perspective"),
        ]

        for text, value in transforms:
            ctk.CTkRadioButton(
                self.control_frame,
                text=text,
                variable=self.transform_var,
                value=value,
                command=self.on_transform_change
            ).pack(anchor="w", padx=20, pady=2)

        # 旋转参数
        self.rotate_frame = ctk.CTkFrame(self.control_frame)
        self.rotate_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.rotate_frame, text="旋转角度 (度)", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.angle = ctk.DoubleVar(value=0)
        slider_angle = ctk.CTkSlider(
            self.rotate_frame,
            from_=-180,
            to=180,
            number_of_steps=360,
            variable=self.angle,
            command=self.apply_transform
        )
        slider_angle.pack(fill="x", padx=10)
        self.angle_label = ctk.CTkLabel(self.rotate_frame, text="0°")
        self.angle_label.pack()

        ctk.CTkLabel(self.rotate_frame, text="缩放比例", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.scale_rotate = ctk.DoubleVar(value=1.0)
        slider_scale = ctk.CTkSlider(
            self.rotate_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            variable=self.scale_rotate,
            command=self.apply_transform
        )
        slider_scale.pack(fill="x", padx=10)
        self.scale_label = ctk.CTkLabel(self.rotate_frame, text="1.0x")
        self.scale_label.pack()

        # 缩放参数
        self.scale_frame = ctk.CTkFrame(self.control_frame)
        self.scale_frame.pack(fill="x", padx=10, pady=5)
        self.scale_frame.pack_forget()

        ctk.CTkLabel(self.scale_frame, text="缩放比例", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.scale_factor = ctk.DoubleVar(value=1.0)
        slider = ctk.CTkSlider(
            self.scale_frame,
            from_=0.1,
            to=3.0,
            number_of_steps=29,
            variable=self.scale_factor,
            command=self.apply_transform
        )
        slider.pack(fill="x", padx=10)
        self.scale_factor_label = ctk.CTkLabel(self.scale_frame, text="1.0x")
        self.scale_factor_label.pack()

        # 平移参数
        self.translate_frame = ctk.CTkFrame(self.control_frame)
        self.translate_frame.pack(fill="x", padx=10, pady=5)
        self.translate_frame.pack_forget()

        ctk.CTkLabel(self.translate_frame, text="X方向平移 (像素)", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.translate_x = ctk.IntVar(value=0)
        slider_tx = ctk.CTkSlider(
            self.translate_frame,
            from_=-200,
            to=200,
            number_of_steps=400,
            variable=self.translate_x,
            command=self.apply_transform
        )
        slider_tx.pack(fill="x", padx=10)
        self.tx_label = ctk.CTkLabel(self.translate_frame, text="0")
        self.tx_label.pack()

        ctk.CTkLabel(self.translate_frame, text="Y方向平移 (像素)", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.translate_y = ctk.IntVar(value=0)
        slider_ty = ctk.CTkSlider(
            self.translate_frame,
            from_=-200,
            to=200,
            number_of_steps=400,
            variable=self.translate_y,
            command=self.apply_transform
        )
        slider_ty.pack(fill="x", padx=10)
        self.ty_label = ctk.CTkLabel(self.translate_frame, text="0")
        self.ty_label.pack()

        # 仿射/透视参数
        self.affine_frame = ctk.CTkFrame(self.control_frame)
        self.affine_frame.pack(fill="x", padx=10, pady=5)
        self.affine_frame.pack_forget()

        ctk.CTkLabel(self.affine_frame, text="预设变换", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.preset_var = ctk.StringVar(value="default")

        presets = [
            ("默认(矩形)", "default"),
            ("倾斜", "skew"),
            ("水平拉伸", "stretch_h"),
            ("垂直拉伸", "stretch_v"),
        ]

        for text, value in presets:
            ctk.CTkRadioButton(
                self.affine_frame,
                text=text,
                variable=self.preset_var,
                value=value,
                command=self.apply_transform
            ).pack(anchor="w", padx=20, pady=2)

        # 透视参数
        self.perspective_frame = ctk.CTkFrame(self.control_frame)
        self.perspective_frame.pack(fill="x", padx=10, pady=5)
        self.perspective_frame.pack_forget()

        ctk.CTkLabel(self.perspective_frame, text="预设变换", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))

        self.perspective_preset = ctk.StringVar(value="default")

        p_presets = [
            ("默认(矩形)", "default"),
            ("梯形变形", "trapezoid"),
            ("远小近大", "perspective_3d"),
            ("旋转倾斜", "rotate_skew"),
        ]

        for text, value in p_presets:
            ctk.CTkRadioButton(
                self.perspective_frame,
                text=text,
                variable=self.perspective_preset,
                value=value,
                command=self.apply_transform
            ).pack(anchor="w", padx=20, pady=2)

    def on_transform_change(self):
        """变换类型变化回调"""
        transform = self.transform_var.get()

        # 隐藏所有参数帧
        self.rotate_frame.pack_forget()
        self.scale_frame.pack_forget()
        self.translate_frame.pack_forget()
        self.affine_frame.pack_forget()
        self.perspective_frame.pack_forget()

        # 显示对应的参数帧
        if transform == "rotate":
            self.rotate_frame.pack(fill="x", padx=10, pady=5)
        elif transform == "scale":
            self.scale_frame.pack(fill="x", padx=10, pady=5)
        elif transform == "translate":
            self.translate_frame.pack(fill="x", padx=10, pady=5)
        elif transform == "affine":
            self.affine_frame.pack(fill="x", padx=10, pady=5)
        elif transform == "perspective":
            self.perspective_frame.pack(fill="x", padx=10, pady=5)

        self.apply_transform()

    def setup_image_panel(self):
        """设置图像显示面板"""
        # 创建图像画布
        self.figure = plt.figure(figsize=(10, 5), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_display()

    def apply_transform(self):
        """应用几何变换"""
        if self.original_image is None:
            return

        transform = self.transform_var.get()
        h, w = self.original_image.shape[:2]

        if transform == "rotate":
            angle = self.angle.get()
            scale = self.scale_rotate.get()
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, scale)
            self.processed_image = cv2.warpAffine(self.original_image, M, (w, h))

            # 更新标签
            self.angle_label.configure(text=f"{angle:.0f}°")
            self.scale_label.configure(text=f"{scale:.1f}x")

        elif transform == "scale":
            factor = self.scale_factor.get()
            new_w = int(w * factor)
            new_h = int(h * factor)
            self.processed_image = cv2.resize(self.original_image, (new_w, new_h))
            self.scale_factor_label.configure(text=f"{factor:.1f}x")

        elif transform == "translate":
            tx = self.translate_x.get()
            ty = self.translate_y.get()
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            self.processed_image = cv2.warpAffine(self.original_image, M, (w, h))

            self.tx_label.configure(text=str(tx))
            self.ty_label.configure(text=str(ty))

        elif transform == "affine":
            preset = self.preset_var.get()

            # 原始三个点
            src_pts = np.float32([[80, 80], [320, 80], [80, 320]])

            if preset == "default":
                dst_pts = np.float32([[80, 80], [320, 80], [80, 320]])
            elif preset == "skew":
                dst_pts = np.float32([[120, 80], [340, 80], [40, 320]])
            elif preset == "stretch_h":
                dst_pts = np.float32([[40, 80], [360, 80], [80, 320]])
            elif preset == "stretch_v":
                dst_pts = np.float32([[80, 40], [320, 40], [80, 360]])

            M = cv2.getAffineTransform(src_pts, dst_pts)
            self.processed_image = cv2.warpAffine(self.original_image, M, (w, h))

        elif transform == "perspective":
            preset = self.perspective_preset.get()

            # 原始四个角点
            src_pts = np.float32([[80, 80], [320, 80], [80, 320], [320, 320]])

            if preset == "default":
                dst_pts = np.float32([[80, 80], [320, 80], [80, 320], [320, 320]])
            elif preset == "trapezoid":
                dst_pts = np.float32([[120, 40], [280, 40], [40, 360], [360, 360]])
            elif preset == "perspective_3d":
                dst_pts = np.float32([[40, 60], [360, 80], [80, 340], [300, 360]])
            elif preset == "rotate_skew":
                dst_pts = np.float32([[60, 40], [340, 100], [100, 300], [280, 360]])

            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            self.processed_image = cv2.warpPerspective(self.original_image, M, (w, h))

        self.update_display()

    def update_display(self):
        """更新图像显示"""
        plt.clf()

        plt.subplot(121)
        if self.original_image is not None:
            plt.imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        plt.title('原图', fontsize=11)
        plt.axis('off')

        plt.subplot(122)
        if self.processed_image is not None:
            plt.imshow(cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB))
            transform = self.transform_var.get()
            transform_names = {
                "rotate": "旋转+缩放",
                "scale": "缩放",
                "translate": "平移",
                "affine": "仿射变换",
                "perspective": "透视变换"
            }
            plt.title(f'{transform_names.get(transform, "变换结果")}', fontsize=11)
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
                self.apply_transform()
                messagebox.showinfo("成功", f"已加载图像: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "无法加载图像文件")


def main():
    """主函数"""
    app = GeometryGUI()
    app.mainloop()


if __name__ == "__main__":
    main()