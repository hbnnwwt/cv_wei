# -*- coding: utf-8 -*-
"""
Modular Recognition Engine Example Code
Week 9: System Architecture and Group Development
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class QuestionType(Enum):
    """Question type enumeration"""
    CHOICE = "choice"
    JUDGE = "judge"
    ESSAY = "essay"


@dataclass
class RecognitionResult:
    """Recognition result"""
    text: str
    confidence: float
    question_type: QuestionType
    raw_data: Dict = None


class RecognizerInterface(ABC):
    """Recognizer interface"""

    @abstractmethod
    def recognize(self, image, roi=None):
        pass

    @abstractmethod
    def get_supported_types(self):
        pass


# ============================================================
# Recognition Engine Core Implementation
# ============================================================

class RecognitionEngine:
    """Modular recognition engine"""

    def __init__(self):
        self.recognizers = {
            qt: [] for qt in QuestionType
        }
        self.strategy = "best_confidence"

    def register(self, recognizer):
        """Register a recognizer"""
        for qtype in recognizer.get_supported_types():
            self.recognizers[qtype].append(recognizer)
        return self

    def recognize(self, image, question_type, roi=None):
        """Execute recognition"""
        recognizers = self.recognizers.get(question_type, [])
        if not recognizers:
            raise ValueError(f"No recognizer found for {question_type}")

        results = [r.recognize(image, roi) for r in recognizers]
        return self._select_best_result(results)

    def _select_best_result(self, results):
        """Select the best result"""
        return max(results, key=lambda r: r.confidence)

    def set_strategy(self, strategy):
        """Set selection strategy"""
        self.strategy = strategy


# ============================================================
# Choice Question Recognizer Implementation
# ============================================================

class ChoiceRecognizer:
    """Choice question answer sheet recognizer"""

    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.name = "ChoiceRecognizer"

    def get_supported_types(self):
        return [QuestionType.CHOICE]

    def recognize(self, image, roi=None):
        """Recognize choice question answers"""
        if roi:
            x, y, w, h = roi
            image = image[y:y+h, x:x+w]

        options = self._detect_options(image)
        filled = self._find_filled_options(options)

        answer = ",".join(filled) if filled else "No answer"
        confidence = self._calculate_confidence(filled, options)

        return RecognitionResult(
            text=answer,
            confidence=confidence,
            question_type=QuestionType.CHOICE
        )

    def _detect_options(self, image):
        """Detect option regions"""
        # Grayscale + binarization + contour detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def _find_filled_options(self, options):
        """Find filled options"""
        filled = []
        for i, contour in enumerate(options):
            area = cv2.contourArea(contour)
            if area > 100:  # Threshold check
                filled.append(chr(65 + i))  # A, B, C, D...
        return filled

    def _calculate_confidence(self, filled, options):
        """Calculate confidence"""
        if not filled:
            return 0.0
        # Simplified calculation
        return min(0.95, 0.7 + 0.1 * len(filled))


# ============================================================
# Judge Question Recognizer Implementation
# ============================================================

class JudgeRecognizer:
    """Judge question symbol recognizer"""

    def __init__(self):
        self.name = "JudgeRecognizer"
        self.templates = {
            "T": self._load_template("true.png"),
            "F": self._load_template("false.png")
        }

    def _load_template(self, path):
        """Load template"""
        return cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    def get_supported_types(self):
        return [QuestionType.JUDGE]

    def recognize(self, image, roi=None):
        """Recognize judge question symbols"""
        if roi:
            x, y, w, h = roi
            image = image[y:y+h, x:x+w]

        symbol = self._analyze_symbol(image)
        best_match, score = self._match_template(symbol)

        return RecognitionResult(
            text=best_match,
            confidence=score,
            question_type=QuestionType.JUDGE
        )

    def _analyze_symbol(self, image):
        """Analyze symbol features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return {"contours": contours}

    def _match_template(self, symbol):
        """Template matching"""
        best = "?"
        best_score = 0.5
        for name, template in self.templates.items():
            score = self._calculate_similarity(symbol, template)
            if score > best_score:
                best = name
                best_score = score
        return best, best_score

    def _calculate_similarity(self, symbol, template):
        """Calculate similarity"""
        return 0.8  # Simplified return


# ============================================================
# Essay Question Recognizer Implementation
# ============================================================

class EssayRecognizer:
    """Essay question OCR recognizer"""

    def __init__(self, use_gpu=False):
        self.name = "EssayRecognizer"
        self.use_gpu = use_gpu
        self.ocr = self._init_ocr()

    def _init_ocr(self):
        """Initialize OCR engine"""
        try:
            from paddleocr import PaddleOCR
            return PaddleOCR(
                use_angle_cls=True,
                lang="ch",
                use_gpu=self.use_gpu
            )
        except ImportError:
            return None

    def get_supported_types(self):
        return [QuestionType.ESSAY]

    def recognize(self, image, roi=None):
        """OCR recognize handwritten text"""
        if roi:
            x, y, w, h = roi
            image = image[y:y+h, x:x+w]

        if self.ocr is None:
            return RecognitionResult(
                text="OCR engine not initialized",
                confidence=0.0,
                question_type=QuestionType.ESSAY
            )

        result = self.ocr.ocr(image, cls=True)
        text = self._extract_text(result)
        confidence = self._average_confidence(result)

        return RecognitionResult(
            text=text,
            confidence=confidence,
            question_type=QuestionType.ESSAY
        )

    def _extract_text(self, result):
        """Extract text"""
        texts = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    texts.append(line[1][0] if isinstance(line[1], list) else line[1])
        return "\n".join(texts)

    def _average_confidence(self, result):
        """Calculate average confidence"""
        if not result or not result[0]:
            return 0.0
        confs = []
        for line in result[0]:
            if line and len(line) >= 2:
                conf = line[1][1] if isinstance(line[1], list) else 0.5
                confs.append(conf)
        return sum(confs) / len(confs) if confs else 0.0


# ============================================================
# Algorithm Registration and Discovery Mechanism
# ============================================================

class RecognizerRegistry:
    """Recognizer registry"""

    def __init__(self):
        self.recognizers = {}

    def register(self, name, recognizer_class):
        """Register recognizer class"""
        self.recognizers[name] = recognizer_class

    def create(self, name, **kwargs):
        """Create recognizer instance"""
        if name not in self.recognizers:
            raise ValueError(f"Unknown recognizer: {name}")
        return self.recognizers[name](**kwargs)

    def list_recognizers(self):
        """List all available recognizers"""
        return list(self.recognizers.keys())


# ============================================================
# Algorithm Selection Strategy
# ============================================================

class BestConfidenceStrategy:
    """Select result with highest confidence"""

    def select(self, results):
        return max(results, key=lambda r: r.confidence)


class VotingStrategy:
    """Majority voting strategy"""

    def select(self, results):
        from collections import Counter
        texts = [r.text for r in results]
        winner = Counter(texts).most_common(1)[0][0]

        winners = [r for r in results if r.text == winner]
        avg_conf = sum(r.confidence for r in winners) / len(winners)

        # Return first winner's result
        return winners[0]


# ============================================================
# Result Fusion and Confidence Evaluation
# ============================================================

class ResultFusion:
    """Result fusion"""

    @staticmethod
    def weighted_fusion(results, weights):
        """Weighted fusion of multiple results"""
        total_weight = sum(weights)
        weighted_conf = sum(
            r.confidence * w for r, w in zip(results, weights)
        ) / total_weight

        best = max(results, key=lambda r: r.confidence)
        return RecognitionResult(
            text=best.text,
            confidence=weighted_conf,
            question_type=best.question_type
        )

    @staticmethod
    def calculate_overall_confidence(results):
        """Calculate overall confidence (geometric mean)"""
        if not results:
            return 0.0
        import math
        product = math.prod(r.confidence for r in results)
        return product ** (1 / len(results))


# ============================================================
# Confidence Threshold and Fallback Strategy
# ============================================================

class ConfidenceBasedFallback:
    """Confidence-based fallback strategy"""

    def __init__(self, engine, threshold=0.8):
        self.engine = engine
        self.threshold = threshold

    def recognize_with_fallback(self, image, question_type):
        """Recognition with fallback"""
        result = self.engine.recognize(image, question_type)

        response = {
            "result": result,
            "confidence": result.confidence,
            "needs_review": False,
            "fallback_used": False
        }

        if result.confidence < self.threshold:
            response["needs_review"] = True

            # Try fallback algorithm
            if question_type == QuestionType.ESSAY:
                # Switch to more precise model
                fallback_result = self._use_precise_model(image)
                if fallback_result.confidence > result.confidence:
                    response["result"] = fallback_result
                    response["fallback_used"] = True
                    response["confidence"] = fallback_result.confidence

        return response

    def _use_precise_model(self, image):
        """Use more precise model"""
        # In real application, switch to more complex model
        return RecognitionResult(
            text="Requires manual review",
            confidence=0.6,
            question_type=QuestionType.ESSAY
        )


# ============================================================
# Engine Usage Complete Example
# ============================================================

def main():
    """Main function example"""
    # 1. Create engine
    engine = RecognitionEngine()

    # 2. Register recognizers
    engine.register(ChoiceRecognizer(threshold=0.5))
    engine.register(JudgeRecognizer())
    engine.register(EssayRecognizer(use_gpu=False))

    # 3. Set selection strategy
    engine.set_strategy("best_confidence")

    # 4. Execute recognition
    # result = engine.recognize(
    #     image=exam_image,
    #     question_type=QuestionType.CHOICE,
    #     roi=(100, 200, 300, 400)
    # )
    # print(f"Result: {result.text}")
    # print(f"Confidence: {result.confidence:.2%}")

    # 5. Batch recognition
    # results = []
    # for region in answer_regions:
    #     result = engine.recognize(image, qtype, region)
    #     results.append(result)


# ============================================================
# Performance Monitoring and Optimization
# ============================================================

class MonitoredEngine(RecognitionEngine):
    """Recognition engine with performance monitoring"""

    def __init__(self):
        super().__init__()
        self.metrics = {
            "total_calls": 0,
            "total_time": 0.0,
            "by_type": {}
        }

    def recognize(self, image, question_type, roi=None):
        """Recognition with monitoring"""
        import time

        start = time.time()
        result = super().recognize(image, question_type, roi)
        elapsed = time.time() - start

        # Record metrics
        self.metrics["total_calls"] += 1
        self.metrics["total_time"] += elapsed

        if question_type not in self.metrics["by_type"]:
            self.metrics["by_type"][question_type] = {
                "count": 0,
                "time": 0.0
            }
        self.metrics["by_type"][question_type]["count"] += 1
        self.metrics["by_type"][question_type]["time"] += elapsed

        return result

    def get_report(self):
        """Get performance report"""
        return {
            "total_calls": self.metrics["total_calls"],
            "total_time_sec": round(self.metrics["total_time"], 2),
            "avg_time_sec": round(
                self.metrics["total_time"] / self.metrics["total_calls"], 4
            ) if self.metrics["total_calls"] > 0 else 0
        }


if __name__ == "__main__":
    main()
