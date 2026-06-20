"""
截图区域选择窗口
全屏透明遮罩，鼠标拖拽选择区域
"""
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage
from PIL import Image
from io import BytesIO


class ScreenshotWindow(QWidget):
    """截图区域选择窗口"""

    # 信号：截图完成，传递 PIL Image
    screenshot_taken = pyqtSignal(object)
    screenshot_cancelled = pyqtSignal()

    def __init__(self, full_screen_pixmap: QPixmap):
        super().__init__()
        self.full_screen_pixmap = full_screen_pixmap
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False

        self._init_window()

    def _init_window(self):
        """初始化窗口：全屏、无边框、置顶"""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setCursor(Qt.CrossCursor)

        # 全屏显示
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.showFullScreen()
        self.activateWindow()
        self.raise_()

    def paintEvent(self, event):
        """绘制截图界面"""
        painter = QPainter(self)

        # 绘制全屏截图作为背景
        painter.drawPixmap(0, 0, self.full_screen_pixmap)

        # 半透明遮罩
        overlay = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay)

        if self.start_pos and self.end_pos:
            # 计算选区
            rect = QRect(self.start_pos, self.end_pos).normalized()

            # 选区内显示原图（去掉遮罩）
            painter.drawPixmap(rect, self.full_screen_pixmap, rect)

            # 选区边框（淡蓝色主题）
            pen = QPen(QColor(90, 168, 247), 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 显示尺寸信息
            size_text = f"{rect.width()} × {rect.height()}"
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(
                rect.x(), rect.y() - 8,
                size_text
            )

        painter.end()

    def mousePressEvent(self, event):
        """鼠标按下：开始选择"""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动：更新选区"""
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放：完成选择"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_pos = event.pos()

            rect = QRect(self.start_pos, self.end_pos).normalized()

            # 选区太小则取消
            if rect.width() < 5 or rect.height() < 5:
                self.start_pos = None
                self.end_pos = None
                self.update()
                return

            # 从原图中裁剪选区
            cropped_pixmap = self.full_screen_pixmap.copy(rect)
            pil_img = self._pixmap_to_pil(cropped_pixmap)

            self.screenshot_taken.emit(pil_img)
            self.close()

    def keyPressEvent(self, event):
        """按键处理：ESC 取消截图"""
        if event.key() == Qt.Key_Escape:
            self.screenshot_cancelled.emit()
            self.close()

    @staticmethod
    def _pixmap_to_pil(pixmap: QPixmap) -> Image.Image:
        """QPixmap 转 PIL Image"""
        qimage = pixmap.toImage()
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        img = Image.frombytes(
            "RGBA",
            (qimage.width(), qimage.height()),
            bytes(ptr),
            "raw", "BGRA"
        )
        return img.convert("RGB")
