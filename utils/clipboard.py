"""
剪贴板工具模块
支持将图片/文本复制到系统剪贴板
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
from io import BytesIO


def copy_image_to_clipboard(img: Image.Image):
    """
    将 PIL Image 复制到系统剪贴板
    :param img: PIL Image 对象
    """
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication 未初始化，请先创建 QApplication")

    buffer = BytesIO()
    img.convert("RGBA").save(buffer, format="PNG")
    qimage = QImage()
    qimage.loadFromData(buffer.getvalue())
    pixmap = QPixmap.fromImage(qimage)

    clipboard = app.clipboard()
    clipboard.setPixmap(pixmap)


def copy_text_to_clipboard(text: str):
    """
    将文本复制到系统剪贴板
    :param text: 要复制的文字
    """
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication 未初始化，请先创建 QApplication")

    clipboard = app.clipboard()
    clipboard.setText(text)


def get_image_from_clipboard() -> Image.Image:
    """
    从剪贴板读取图片
    :return: PIL Image 对象，如果没有图片返回 None
    """
    app = QApplication.instance()
    if app is None:
        return None

    clipboard = app.clipboard()
    pixmap = clipboard.pixmap()
    if pixmap.isNull():
        return None

    # QPixmap -> bytes -> PIL Image
    buffer = BytesIO()
    qimage = pixmap.toImage()
    ptr = qimage.bits()
    ptr.setsize(qimage.byteCount())
    img = Image.frombytes("RGBA", (qimage.width(), qimage.height()), bytes(ptr), "raw", "BGRA")
    return img
