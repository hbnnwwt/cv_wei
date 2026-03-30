# -*- coding: utf-8 -*-
"""
Week 01 批量处理 - GUI版本
==============================
带有参数调整功能的交互式演示
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
import numpy as np
import os
import sys
import random
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

from gui_config import get_appearance_mode
current_mode = get_appearance_mode()
ctk.set_appearance_mode(current_mode)
ctk.set_default_color_theme("blue")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class BatchProcessingGUI(ctk.CTk):
    """批量处理GUI - 带有参数调整功能"""

    def __init__(self):
        super().__init__()
        self.title("批量处理与结果输出 - 参数调整演示")
        self.geometry("1200x800")

        # 批量处理参数
        self.num_papers = 10
        self.num_questions = 10
        self.confidence_threshold = 0.7

        # 测试图像和结果
        self.test_images = []
        self.results = []

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()

    def on_closing(self):
        self.destroy()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)

        self.title_label = ctk.CTkLabel(
            top_frame,
            text="批量处理与结果输出 - 参数调整演示",
            font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 左侧控制面板
        self.control_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.control_frame.pack(side="left", fill="y", padx=(0, 10))

        # 右侧结果显示
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(side="right", fill="both", expand=True)

        self.setup_control()
        self.setup_result_panel()

    def setup_control(self):
        """设置控制面板"""
        ctk.CTkLabel(self.control_frame, text="参数设置",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # 试卷数量
        ctk.CTkLabel(self.control_frame, text="生成试卷数量:").pack(pady=(10, 0))
        self.papers_slider = ctk.CTkSlider(self.control_frame, from_=1, to=20, number_of_steps=19)
        self.papers_slider.set(self.num_papers)
        self.papers_slider.pack(fill="x", padx=20)
        self.papers_label = ctk.CTkLabel(self.control_frame, text=f"{self.num_papers}")
        self.papers_label.pack()

        # 题目数量
        ctk.CTkLabel(self.control_frame, text="每卷题目数量:").pack(pady=(10, 0))
        self.questions_slider = ctk.CTkSlider(self.control_frame, from_=5, to=20, number_of_steps=15)
        self.questions_slider.set(self.num_questions)
        self.questions_slider.pack(fill="x", padx=20)
        self.questions_label = ctk.CTkLabel(self.control_frame, text=f"{self.num_questions}")
        self.questions_label.pack()

        # 置信度阈值
        ctk.CTkLabel(self.control_frame, text="置信度阈值:").pack(pady=(10, 0))
        self.confidence_slider = ctk.CTkSlider(self.control_frame, from_=0.5, to=0.99, number_of_steps=49)
        self.confidence_slider.set(self.confidence_threshold)
        self.confidence_slider.pack(fill="x", padx=20)
        self.confidence_label = ctk.CTkLabel(self.control_frame, text=f"{self.confidence_threshold:.2f}")
        self.confidence_label.pack()

        # 应用按钮
        ctk.CTkButton(self.control_frame, text="应用参数",
                     command=self.apply_params).pack(pady=20, fill="x", padx=20)

        # 操作按钮
        ctk.CTkLabel(self.control_frame, text="操作",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        ctk.CTkButton(self.control_frame, text="生成测试试卷",
                     command=self.generate_test_papers).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.control_frame, text="开始批量处理",
                     command=self.process_batch).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.control_frame, text="显示统计报告",
                     command=self.show_statistics).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(self.control_frame, text="清空结果",
                     command=self.clear_results).pack(fill="x", padx=20, pady=5)

    def setup_result_panel(self):
        """设置结果显示面板"""
        ctk.CTkLabel(self.result_frame, text="处理结果",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.result_text = ctk.CTkTextbox(self.result_frame, height=500)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_text.insert("1.0",
            "欢迎使用批量处理演示系统！\n\n"
            "请按以下步骤操作：\n"
            "1. 调整参数（试卷数量、题目数量等）\n"
            "2. 点击「生成测试试卷」创建模拟数据\n"
            "3. 点击「开始批量处理」进行识别\n"
            "4. 点击「显示统计报告」查看汇总\n")

    def apply_params(self):
        """应用参数"""
        self.num_papers = int(self.papers_slider.get())
        self.num_questions = int(self.questions_slider.get())
        self.confidence_threshold = self.confidence_slider.get()

        self.papers_label.configure(text=f"{self.num_papers}")
        self.questions_label.configure(text=f"{self.num_questions}")
        self.confidence_label.configure(text=f"{self.confidence_threshold:.2f}")

        messagebox.showinfo("参数已更新",
            f"试卷数量: {self.num_papers}\n"
            f"题目数量: {self.num_questions}\n"
            f"置信度阈值: {self.confidence_threshold:.2f}")

    def generate_test_papers(self):
        """生成测试试卷图像"""
        self.test_images = []

        for i in range(self.num_papers):
            # 创建随机试卷图像
            img = np.random.randint(150, 220, (480, 640, 3), dtype=np.uint8)

            # 添加一些标记模拟答题
            for j in range(self.num_questions):
                row = 80 + j * 35
                col = 100 + random.randint(0, 3) * 120
                # 随机填涂
                if random.random() > 0.3:
                    cv2.circle(img, (col, row), 12, (0, 0, 0), -1)

            self.test_images.append(img)

        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0",
            f"已生成 {self.num_papers} 张测试试卷图像！\n\n"
            f"每张试卷包含 {self.num_questions} 道题目。\n"
            f"图像大小: 640x480\n\n"
            f"点击「开始批量处理」进行识别...")

        messagebox.showinfo("完成", f"已生成 {self.num_papers} 张测试试卷！")

    def process_batch(self):
        """批量处理"""
        if not self.test_images:
            messagebox.showwarning("警告", "请先生成测试试卷！")
            return

        self.results = []
        options = ['A', 'B', 'C', 'D']

        for i, img in enumerate(self.test_images):
            # 模拟答案检测
            answers = []
            for q in range(self.num_questions):
                # 随机选择答案和置信度
                answer = random.choice(options)
                confidence = random.uniform(0.6, 0.99)

                # 根据阈值过滤
                if confidence >= self.confidence_threshold:
                    answers.append({
                        'question': q + 1,
                        'answer': answer,
                        'confidence': confidence
                    })

            self.results.append({
                'file': f'paper_{i+1:03d}.jpg',
                'success': True,
                'answers': answers,
                'total_answers': len(answers),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })

        self.display_results()
        messagebox.showinfo("完成", f"批量处理完成！共处理 {len(self.results)} 份试卷")

    def display_results(self):
        """显示处理结果"""
        self.result_text.delete("1.0", "end")

        self.result_text.insert("end", "=" * 60 + "\n")
        self.result_text.insert("end", "批量处理结果\n")
        self.result_text.insert("end", "=" * 60 + "\n\n")

        for result in self.results:
            self.result_text.insert("end", f"文件: {result['file']}\n")
            self.result_text.insert("end", f"时间: {result['timestamp']}\n")
            self.result_text.insert("end", f"识别题数: {result['total_answers']}/{self.num_questions}\n")

            if result['answers']:
                answers_str = ", ".join(
                    f"Q{a['question']}:{a['answer']}({a['confidence']:.0%})"
                    for a in result['answers'][:5]
                )
                self.result_text.insert("end", f"答案: {answers_str}")
                if len(result['answers']) > 5:
                    self.result_text.insert("end", "...")
            else:
                self.result_text.insert("end", "答案: 无")

            self.result_text.insert("end", "\n" + "-" * 40 + "\n\n")

    def show_statistics(self):
        """显示统计报告"""
        if not self.results:
            messagebox.showwarning("警告", "请先进行批量处理！")
            return

        total = len(self.results)
        total_answers = sum(r['total_answers'] for r in self.results)
        avg_answers = total_answers / total if total > 0 else 0

        # 统计答案分布
        answer_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for r in self.results:
            for a in r['answers']:
                answer_counts[a['answer']] = answer_counts.get(a['answer'], 0) + 1

        self.result_text.delete("1.0", "end")

        self.result_text.insert("end", "=" * 60 + "\n")
        self.result_text.insert("end", "统计报告\n")
        self.result_text.insert("end", "=" * 60 + "\n\n")

        self.result_text.insert("end", f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        self.result_text.insert("end", "【总体统计】\n")
        self.result_text.insert("end", f"  总试卷数: {total}\n")
        self.result_text.insert("end", f"  总识别题数: {total_answers}\n")
        self.result_text.insert("end", f"  平均每份: {avg_answers:.1f} 题\n")
        self.result_text.insert("end", f"  置信度阈值: {self.confidence_threshold:.0%}\n\n")

        self.result_text.insert("end", "【答案分布】\n")
        for opt in ['A', 'B', 'C', 'D']:
            count = answer_counts.get(opt, 0)
            pct = count / total_answers * 100 if total_answers > 0 else 0
            self.result_text.insert("end", f"  {opt}: {count} ({pct:.1f}%)\n")

        self.result_text.insert("end", "\n【柱状图】\n")
        max_count = max(answer_counts.values()) if answer_counts else 1
        for opt in ['A', 'B', 'C', 'D']:
            count = answer_counts.get(opt, 0)
            bar_len = int(count / max_count * 30) if max_count > 0 else 0
            self.result_text.insert("end", f"  {opt}: {'█' * bar_len} {count}\n")

        messagebox.showinfo("统计报告", "统计报告已生成！")

    def clear_results(self):
        """清空结果"""
        self.test_images = []
        self.results = []
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "结果已清空！")


def main():
    app = BatchProcessingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
