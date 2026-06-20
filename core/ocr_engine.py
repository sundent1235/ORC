"""
OCR 文字识别模块
使用 RapidOCR（基于 PaddleOCR + ONNX Runtime）
支持中英文，大图小图均可正确识别
"""
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR


class OCREngine:
    """OCR 文字识别引擎"""

    def __init__(self):
        self._ocr = None

    @property
    def ocr(self):
        """延迟加载 OCR 模型（首次调用时加载，较慢）"""
        if self._ocr is None:
            self._ocr = RapidOCR()
        return self._ocr

    def recognize_text(self, img: Image.Image) -> str:
        """
        识别图片中的文字
        :param img: PIL Image 对象
        :return: 识别到的文字内容（每行用换行分隔）
        """
        result, _ = self.ocr(np.array(img))
        if not result:
            return ""
        # result: list of [box, text, confidence]
        # 按位置排序（从上到下、从左到右）
        lines = sorted(result, key=lambda r: (r[0][0][1] // 10, r[0][0][0]))
        return "\n".join(text for _, text, _ in lines if text.strip())

    def recognize_from_file(self, filepath: str) -> str:
        """从文件路径识别文字"""
        img = Image.open(filepath)
        return self.recognize_text(img)

    def recognize_with_positions(self, img: Image.Image) -> list:
        """
        识别文字及其位置（用于在图上标注）
        :return: [(text, bbox), ...]
            bbox 为 [x1, y1, x2, y2] 格式
        """
        result, _ = self.ocr(np.array(img))
        if not result:
            return []

        results = []
        for box, text, confidence in result:
            # box 是四点坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            # 转为 [x1, y1, x2, y2] 格式
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            bbox = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
            results.append((text, bbox))

        return results
