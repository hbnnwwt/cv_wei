# -*- coding: utf-8 -*-
"""Week 01 气泡检测演示 - GUI版本使用 customtkinter 构建的图形界面"""



import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import os
import sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
from gui_config import get_appearance_mode
current_mode = get_appearance_mode()
ctk.set_appearance_mode(current_mode)
ctk.set_default_color_theme("blue")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
class BubbleDetectionGUI(ctk.CTk):
    """气泡检测演示GUI"""
    DEFAULT_ROWS = 5
    DEFAULT_COLS = 4
    OPTIONS = ['A', 'B', 'C', 'D']
    START_X = 30
    START_Y = 30
    DEFAULT_GAP_X = 80
    DEFAULT_GAP_Y = 50
    DEFAULT_BUBBLE_RADIUS = 15
    GAP_MARGIN = 5  # 气泡周围的边距
    def __init__(self):
        super().__init__()
        self.title("Bubble Detection Demo")
        self.geometry("1200x800")
        self.cell_size = self.DEFAULT_BUBBLE_RADIUS
        self.gap = self.GAP_MARGIN
        self.threshold = 0.3
        
        # 根据 cell_size 计算气泡间距
        self.gap_x = self.cell_size * 2 + self.gap * 2
        self.gap_y = int(self.cell_size * 1.5)
        self.start_x = self.START_X
        self.start_y = self.START_Y
        self.test_image = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()
        self.regenerate_test()
    def on_closing(self):
        try:
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'figure'):
                plt.close(self.figure)
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
        finally:
            self.destroy()
    def create_test_bubbles(self):
        rows = self.DEFAULT_ROWS
        cols = self.DEFAULT_COLS
        img_height = self.start_y * 2 + rows * self.gap_y
        img_width = self.start_x * 2 + cols * self.gap_x
        
        img = np.ones((img_height, img_width), dtype=np.uint8) * 255
        radius = self.cell_size
        fill_radius = radius - 2
        
        for i in range(rows):
            for j in range(cols):
                x = self.start_x + j * self.gap_x
                y = self.start_y + i * self.gap_y
                cv2.circle(img, (x, y), radius, 0, 2)
                filled = (i + j) % 2 == 0
                if filled:
                    cv2.circle(img, (x, y), fill_radius, 0, -1)
        return img
    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        self.title_label = ctk.CTkLabel(
            top_frame,
            text="气泡检测演示 - 智能阅卷系统",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.control_frame = ctk.CTkFrame(self.main_frame, width=280)
        self.control_frame.pack(side="left", fill="y", padx=(0, 10))
        self.image_frame = ctk.CTkFrame(self.main_frame)
        self.image_frame.pack(side="right", fill="both", expand=True)
        self.setup_control()
        self.setup_image_panel()
    def setup_control(self):
        ctk.CTkLabel(self.control_frame, text="参数设置", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.control_frame, text="气泡大小:").pack(pady=(10, 0))
        self.size_slider = ctk.CTkSlider(self.control_frame, from_=20, to=50, number_of_steps=30)
        self.size_slider.set(self.cell_size)
        self.size_slider.pack(fill="x", padx=20)
        self.size_label = ctk.CTkLabel(self.control_frame, text=f"{self.cell_size}像素")
        self.size_label.pack()
        ctk.CTkLabel(self.control_frame, text="填涂阈值:").pack(pady=(10, 0))
        self.thresh_slider = ctk.CTkSlider(self.control_frame, from_=0.1, to=0.7, number_of_steps=12)
        self.thresh_slider.set(self.threshold)
        self.thresh_slider.pack(fill="x", padx=20)
        self.thresh_label = ctk.CTkLabel(self.control_frame, text=f"{self.threshold:.1f}")
        self.thresh_label.pack()
        ctk.CTkButton(self.control_frame, text="应用参数", command=self.apply_params).pack(pady=20, fill="x", padx=20)
        ctk.CTkLabel(self.control_frame, text="操作", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        ctk.CTkButton(self.control_frame, text="重新生成测试图像", command=self.regenerate_test).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="手动填涂演示", command=self.manual_fill).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self.control_frame, text="批量检测所有气泡", command=self.detect_all).pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(self.control_frame, text="检测结果", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        self.result_text = ctk.CTkTextbox(self.control_frame, height=100)
        self.result_text.pack(fill="x", padx=20, pady=10)
    def setup_image_panel(self):
        self.figure = plt.figure(figsize=(8, 6), facecolor="white")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.image_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    def show_image(self, img):
        if img is None:
            logger.error("Cannot display None image")
            return
        plt.clf()
        plt.imshow(img, cmap="gray")
        plt.title("Bubble Detection - White=Empty, Black=Filled", color="black")
        plt.axis("off")
        plt.tight_layout()
        self.canvas.draw()
    def apply_params(self):
        new_size = int(self.size_slider.get())
        new_threshold = self.thresh_slider.get()
        
        if new_size < 10 or new_size > 100:
            messagebox.showerror("Error", "Bubble size must be between 10 and 100")
            return
        if new_threshold < 0.0 or new_threshold > 1.0:
            messagebox.showerror("Error", "Threshold must be between 0.0 and 1.0")
            return
        
        self.cell_size = new_size
        self.threshold = new_threshold
        self.gap_x = self.cell_size * 2 + self.gap * 2
        self.gap_y = int(self.cell_size * 1.5)
        
        self.size_label.configure(text=f"{self.cell_size}像素")
        self.thresh_label.configure(text=f"{self.threshold:.1f}")
        
        logger.info(f"Parameters updated: cell_size={self.cell_size}, threshold={self.threshold}")
        messagebox.showinfo("参数已更新", f"气泡大小: {self.cell_size} 像素\n填涂阈值: {round(self.threshold, 1)}")

        # 重要：参数更新后重新生成测试图像
        self.regenerate_test()
    def regenerate_test(self):
        try:
            self.test_image = self.create_test_bubbles()
            self.show_image(self.test_image)
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "测试图像已重新生成")
            logger.info("Test image regenerated")
        except Exception as e:
            logger.error(f"Failed to regenerate test image: {e}")
            messagebox.showerror("Error", f"生成测试图像失败: {e}")
    def manual_fill(self):
        if self.test_image is None:
            messagebox.showwarning("Warning", "请先生成测试图像")
            return
            
        radius = self.cell_size - 3
        row, col1, col2 = 1, 1, 2
        x1 = self.start_x + col1 * self.gap_x
        y1 = self.start_y + row * self.gap_y
        x2 = self.start_x + col2 * self.gap_x
        y2 = self.start_y + row * self.gap_y
        
        if (y1 - radius >= 0 and y1 + radius < self.test_image.shape[0] and
            x1 - radius >= 0 and x1 + radius < self.test_image.shape[1]):
            cv2.circle(self.test_image, (x1, y1), radius, 0, -1)
        if (y2 - radius >= 0 and y2 + radius < self.test_image.shape[0] and
            x2 - radius >= 0 and x2 + radius < self.test_image.shape[1]):
            cv2.circle(self.test_image, (x2, y2), radius, 0, -1)
            
        self.show_image(self.test_image)
        # 手动填涂后执行检测（不重复显示messagebox）
        self._run_detection()
    def _calculate_bubble_position(self, row: int, col: int):
        x = self.start_x + col * self.gap_x
        y = self.start_y + row * self.gap_y
        return x, y
    def _extract_bubble_region(self, x: int, y: int, img: np.ndarray):
        radius = self.cell_size
        half_size = radius + self.gap  # 使用配置的边距
        y_min = max(0, y - half_size)
        y_max = min(img.shape[0], y + half_size)
        x_min = max(0, x - half_size)
        x_max = min(img.shape[1], x + half_size)
        return img[y_min:y_max, x_min:x_max]
    def _is_bubble_filled(self, bubble: np.ndarray) -> bool:
        if bubble.size == 0:
            return False
        # 根据气泡大小动态计算中心区域
        center_margin = max(3, int(self.cell_size * 0.15))
        center_start = center_margin
        center_end = min(bubble.shape[0] - center_margin,
                        bubble.shape[1] - center_margin,
                        int(self.cell_size))
        if center_end <= center_start:
            return False
        center = bubble[center_start:center_end, center_start:center_end]
        if center.size == 0:
            return False
        white_pixels = np.sum(center > 200)
        white_ratio = white_pixels / center.size
        return white_ratio < self.threshold
    def detect_all(self):
        """检测所有气泡并显示结果"""
        if self.test_image is None:
            messagebox.showwarning("Warning", "请先生成测试图像")
            return

        # 执行检测
        self._run_detection()

    def _run_detection(self):
        """执行检测逻辑（内部方法，不显示重复的messagebox）"""
        rows = self.DEFAULT_ROWS
        cols = self.DEFAULT_COLS
        results = []
        answers = []
        try:
            for i in range(rows):
                row_result = []
                selected = None
                for j in range(cols):
                    x, y = self._calculate_bubble_position(i, j)
                    bubble = self._extract_bubble_region(x, y, self.test_image)
                    is_filled = self._is_bubble_filled(bubble)
                    
                    option = self.OPTIONS[j]
                    status = "Filled" if is_filled else "Empty"
                    
                    if is_filled:
                        selected = option
                    row_result.append(f"{option}:{status}")
                results.append(f"Q{i+1}: " + " ".join(row_result))
                if selected:
                    answers.append(f"Q{i+1}: {selected}")
            self._display_results(results, answers, rows)
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            messagebox.showerror("Error", f"检测失败: {e}")
    def _display_results(self, results: list, answers: list, total_rows: int):
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "=== 检测结果 ===\n")

        for r in results:
            self.result_text.insert("end", r + "\n")

        if answers:
            self.result_text.insert("end", "\n=== 检测到的答案 ===\n")

            for a in answers:
                self.result_text.insert("end", a + "\n")
        else:
            self.result_text.insert("end", "\n未检测到任何答案！")

        filled = len(answers)
        empty = total_rows - filled
        self.result_text.insert("end", f"\n总计: 填涂={filled}, 空={empty}")

        answer_str = ", ".join(answers) if answers else "无"
        messagebox.showinfo("完成", f"检测完成！\n答案: {answer_str}\n填涂: {filled}/{total_rows}")


def main():
    try:
        app = BubbleDetectionGUI()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        messagebox.showerror("Critical Error", f"应用程序崩溃: {e}")
if __name__ == "__main__":
    main()