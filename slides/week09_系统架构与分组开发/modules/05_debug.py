# -*- coding: utf-8 -*-
"""
Debug tools module
Provides image debugging and visualization helper functions
"""

import cv2
import os
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any


def save_debug_image(image, name, output_dir="debug"):
    """
    Save debug image to debug directory

    Args:
        image: numpy.ndarray, image to save
        name: str, debug image name prefix
        output_dir: str, output directory name
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    path = os.path.join(output_dir, filename)
    cv2.imwrite(path, image)
    print(f"[DEBUG] Saved: {path}")
    return path


def draw_debug_boxes(image, boxes, labels=None, color=(0, 255, 0)):
    """
    Draw debug boxes on image

    Args:
        image: numpy.ndarray, original image
        boxes: List[Tuple[int, int, int, int]], bounding box list [(x, y, w, h), ...]
        labels: List[str], optional, box labels
        color: Tuple[int, int, int], BGR color

    Returns:
        numpy.ndarray: image with bounding boxes
    """
    result = image.copy()
    for i, box in enumerate(boxes):
        x, y, w, h = box
        cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
        if labels and i < len(labels):
            cv2.putText(result, labels[i], (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return result


def draw_debug_polygons(image, polygons, labels=None, color=(0, 255, 0)):
    """
    Draw debug polygons on image (for contours)

    Args:
        image: numpy.ndarray, original image
        polygons: List[numpy.ndarray], polygon points list
        labels: List[str], optional, polygon labels
        color: Tuple[int, int, int], BGR color

    Returns:
        numpy.ndarray: image with polygons
    """
    result = image.copy()
    for i, polygon in enumerate(polygons):
        if len(polygon) >= 3:
            pts = polygon.reshape(-1, 2).astype(int)
            cv2.polylines(result, [pts], isClosed=True, color=color, thickness=2)
            if labels and i < len(labels):
                cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
                cv2.putText(result, labels[i], (int(cx), int(cy - 10)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return result


def visualize_pipeline_steps(steps: List[Dict[str, Any]]) -> None:
    """
    Visualize pipeline processing steps

    Args:
        steps: List[Dict], each step info containing:
            - 'name': step name
            - 'image': processed image
            - 'time': processing time (optional)
    """
    for i, step in enumerate(steps):
        name = step.get('name', f'Step {i + 1}')
        image = step.get('image')
        time_ms = step.get('time', 0)

        if image is not None:
            cv2.imshow(f"Step {i + 1}: {name}", image)
            print(f"[PIPELINE] Step {i + 1}: {name} ({time_ms:.2f}ms)")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def log_recognition_result(result, module_name="Recognizer"):
    """
    Log recognition result to console

    Args:
        result: RecognitionResult, recognition result
        module_name: str, module name
    """
    print(f"[{module_name}]")
    print(f"  Text: {result.text}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Type: {result.question_type}")


def create_debug_report(image_path, detections, recognitions) -> Dict[str, Any]:
    """
    Create debug report

    Args:
        image_path: str, image path
        detections: List[Dict], detection results
        recognitions: List[Dict], recognition results

    Returns:
        Dict: debug report
    """
    report = {
        'image_path': image_path,
        'timestamp': datetime.now().isoformat(),
        'detections': detections,
        'recognitions': recognitions,
        'total_detections': len(detections),
        'total_recognitions': len(recognitions)
    }

    report_path = os.path.join("debug", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    import json
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[DEBUG] Report saved: {report_path}")
    return report


class DebugPipeline:
    """Debug pipeline manager"""

    def __init__(self, output_dir="debug"):
        self.output_dir = output_dir
        self.steps = []
        os.makedirs(output_dir, exist_ok=True)

    def add_step(self, name, image, info=None):
        """Add processing step"""
        import time
        step = {
            'name': name,
            'image': image.copy() if image is not None else None,
            'time': time.time(),
            'info': info or {}
        }
        self.steps.append(step)
        print(f"[DEBUG] Step added: {name}")

    def save_all_steps(self):
        """Save all step images"""
        for i, step in enumerate(self.steps):
            if step['image'] is not None:
                save_debug_image(step['image'], f"step_{i+1}_{step['name']}", self.output_dir)

    def visualize(self):
        """Visualize all steps"""
        for i, step in enumerate(self.steps):
            if step['image'] is not None:
                cv2.imshow(f"Step {i + 1}: {step['name']}", step['image'])
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            'total_steps': len(self.steps),
            'steps': [s['name'] for s in self.steps],
            'output_dir': self.output_dir
        }
