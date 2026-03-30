# -*- coding: utf-8 -*-
"""
Week 03 教学演示 GUI 启动器
===========================
选择要运行的图形界面演示

使用方法:
    python gui_launcher.py
"""

import customtkinter as ctk
import sys
import os

# 导入配置管理器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gui_config import get_appearance_mode, set_appearance_mode, get_color_theme

# 从配置文件加载设置
current_mode = get_appearance_mode()
current_theme = get_color_theme()
ctk.set_appearance_mode(current_mode)
ctk.set_default_color_theme(current_theme)

# GUI文件列表
GUI_DEMOS = [
    ("gui_01_denoising.py", "去噪演示", "均值滤波/高斯滤波/中值滤波/双边滤波 - 可调核大小"),
    ("gui_02_enhancement.py", "增强演示", "CLAHE/直方图均衡化/Gamma校正 - 可调参数"),
    ("gui_03_binarization.py", "二值化演示", "固定阈值/Otsu/自适应阈值 - 可调阈值参数"),
    ("gui_04_geometry.py", "几何变换演示", "旋转/缩放/仿射/透视 - 可调变换参数"),
]


class LauncherGUI(ctk.CTk):
    """GUI启动器"""

    def __init__(self):
        super().__init__()

        self.title("Week 03 教学演示 - GUI启动器")
        self.geometry("800x600")

        # 添加主题切换按钮
        self.theme_button = None

        self.setup_ui()

    def setup_ui(self):
        # 顶部框架（包含标题和主题切换）
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        # 标题
        ctk.CTkLabel(
            top_frame,
            text="Week 03 图像预处理与增强 - 教学演示",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        # 主题切换按钮
        current_mode = get_appearance_mode()
        mode_text = "Dark Mode" if current_mode == "light" else "Light Mode"

        self.theme_button = ctk.CTkButton(
            top_frame,
            text=mode_text,
            command=self.toggle_theme,
            width=100,
            fg_color="gray" if current_mode == "light" else "#3B8ED0"
        )
        self.theme_button.pack(side="right")

        # 副标题
        ctk.CTkLabel(
            self,
            text="选择要运行的演示程序",
            font=ctk.CTkFont(size=16)
        ).pack(pady=(0, 20))

        # 演示列表
        self.demo_frame = ctk.CTkFrame(self)
        self.demo_frame.pack(fill="both", expand=True, padx=40, pady=20)

        for i, (filename, title, desc) in enumerate(GUI_DEMOS):
            self.add_demo_button(i + 1, filename, title, desc)

        # 底部说明
        ctk.CTkLabel(
            self,
            text="提示: 如果遇到错误，请确保已安装所需依赖:\n  pip install customtkinter opencv-python numpy matplotlib",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=20)

    def add_demo_button(self, num, filename, title, desc):
        """添加演示按钮"""
        frame = ctk.CTkFrame(self.demo_frame)
        frame.pack(fill="x", padx=10, pady=5)

        # 编号
        ctk.CTkLabel(
            frame,
            text=f"{num}",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=40
        ).pack(side="left", padx=10)

        # 标题和描述
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=desc,
            text_color="gray"
        ).pack(anchor="w")

        # 运行按钮
        ctk.CTkButton(
            frame,
            text="运行",
            command=lambda: self.run_demo(filename),
            width=80
        ).pack(side="right", padx=10, pady=10)

    def toggle_theme(self):
        """切换主题"""
        import subprocess
        current = get_appearance_mode()
        new_mode = "dark" if current == "light" else "light"

        # 保存新设置
        set_appearance_mode(new_mode)

        # 更新所有GUI的主题
        self.update_all_gui_theme(new_mode)

        # 重新启动启动器
        self.destroy()
        subprocess.run(f'"{sys.executable}" "{__file__}"', shell=True)

    def update_all_gui_theme(self, mode):
        """更新所有GUI的主题设置（现在从配置文件读取，此方法保留兼容）"""
        # 主题已改为从配置文件读取，无需修改文件
        pass

    def run_demo(self, filename):
        """运行选定的演示"""
        # 隐藏当前窗口
        self.withdraw()

        # 构建完整路径
        demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        if not os.path.exists(demo_path):
            print(f"错误: 找不到文件 {demo_path}")
            self.deiconify()
            return

        # 运行演示
        print(f"启动演示: {filename}")
        import subprocess
        subprocess.run(f'"{sys.executable}" "{demo_path}"', shell=True)

        # 演示结束后重新显示启动器
        self.deiconify()


def check_dependencies():
    """检查依赖是否已安装"""
    missing = []

    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")

    if missing:
        print("缺少必要的依赖库，请运行以下命令安装:")
        print(f"pip install {' '.join(missing)}")
        print()
        return False

    return True


def main():
    """主函数"""
    if not check_dependencies():
        input("按回车键退出...")
        sys.exit(1)

    app = LauncherGUI()
    app.mainloop()


if __name__ == "__main__":
    main()