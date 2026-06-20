"""
OCR 结果展示弹窗
显示截图预览、识别文字和翻译结果
"""
import os
from io import BytesIO

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QComboBox, QScrollArea, QWidget, QSizePolicy,
    QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon

from PIL import Image
from core.translator import Translator
from utils.clipboard import copy_text_to_clipboard

# 图标路径（兼容 PyInstaller 打包）
import sys
if getattr(sys, 'frozen', False):
    _ASSETS_DIR = os.path.join(sys._MEIPASS, 'assets')
else:
    _ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
_ICON_PATH = os.path.join(_ASSETS_DIR, 'icon.png')


class TranslateWorker(QThread):
    """后台翻译线程，避免阻塞 UI"""
    finished = pyqtSignal(str)

    def __init__(self, translator, text):
        super().__init__()
        self.translator = translator
        self.text = text

    def run(self):
        result = self.translator.translate(self.text)
        self.finished.emit(result)


# 淡蓝色主题样式常量
COLOR_PRIMARY = "#5AA8F7"       # 主色调（淡蓝）
COLOR_PRIMARY_DARK = "#3D8FE0"  # 深蓝（悬停/按下）
COLOR_PRIMARY_DEEPER = "#2B78CC"  # 更深蓝（按下）
COLOR_SUCCESS = "#52C47A"       # 成功（清新绿）
COLOR_BG = "#E8F4FD"            # 背景（极淡蓝）
COLOR_CARD = "#FFFFFF"          # 卡片白
COLOR_BORDER = "#B8D9F2"        # 边框（淡蓝灰）
COLOR_TEXT = "#1B3A5C"          # 文字（深蓝灰）
COLOR_TEXT_SUB = "#6B8DB5"      # 副文字（蓝灰）
COLOR_PREVIEW_BG = "#D6EDFB"    # 预览区背景（淡蓝）


class OCRDialog(QDialog):
    """OCR 结果弹窗"""

    STYLESHEET = f"""
        QDialog {{
            background-color: {COLOR_BG};
        }}
        QLabel {{
            color: {COLOR_TEXT};
            font-family: "Microsoft YaHei";
        }}
        QLabel#title {{
            font-size: 18px;
            font-weight: bold;
            color: {COLOR_PRIMARY_DARK};
            padding: 4px 0;
        }}
        QLabel#section {{
            font-size: 12px;
            font-weight: bold;
            color: {COLOR_TEXT_SUB};
            padding: 2px 0;
        }}
        QTextEdit {{
            background-color: {COLOR_CARD};
            border: 1.5px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 10px;
            font-family: "Microsoft YaHei";
            font-size: 13px;
            color: {COLOR_TEXT};
            selection-background-color: {COLOR_PRIMARY};
        }}
        QTextEdit:focus {{
            border-color: {COLOR_PRIMARY};
        }}
        QPushButton {{
            background-color: {COLOR_CARD};
            border: 1.5px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 9px 22px;
            font-family: "Microsoft YaHei";
            font-size: 13px;
            color: {COLOR_TEXT};
            min-width: 90px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_PREVIEW_BG};
            border-color: {COLOR_PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_BORDER};
        }}
        QPushButton#primary {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            font-weight: bold;
        }}
        QPushButton#primary:hover {{
            background-color: {COLOR_PRIMARY_DARK};
        }}
        QPushButton#primary:pressed {{
            background-color: {COLOR_PRIMARY_DEEPER};
        }}
        QPushButton#success {{
            background-color: {COLOR_SUCCESS};
            color: white;
            border: none;
        }}
        QPushButton#success:hover {{
            background-color: #3FB568;
        }}
        QComboBox {{
            background-color: {COLOR_CARD};
            border: 1.5px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 7px 14px;
            font-family: "Microsoft YaHei";
            font-size: 13px;
            color: {COLOR_TEXT};
            min-width: 100px;
        }}
        QComboBox:hover {{
            border-color: {COLOR_PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            border: 1.5px solid {COLOR_BORDER};
            background-color: {COLOR_CARD};
            selection-background-color: {COLOR_PRIMARY};
            selection-color: white;
            outline: none;
        }}
        QScrollArea {{
            border: 1.5px solid {COLOR_BORDER};
            border-radius: 8px;
            background-color: {COLOR_PREVIEW_BG};
        }}
        QScrollBar:vertical {{
            background-color: {COLOR_BG};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {COLOR_BORDER};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {COLOR_PRIMARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.translator = Translator()
        self._pil_img = None
        self._worker = None
        self._init_ui()
        # 设置窗口图标
        if os.path.exists(_ICON_PATH):
            self.setWindowIcon(QIcon(_ICON_PATH))

    def _init_ui(self):
        self.setWindowTitle("ORC 截图识别")
        self.setMinimumSize(680, 640)
        self.resize(720, 680)
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowStaysOnTopHint
            | Qt.WindowMinimizeButtonHint
        )
        self.setStyleSheet(self.STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # ---- 标题 ----
        title = QLabel("截图识别与翻译")
        title.setObjectName("title")
        main_layout.addWidget(title)

        # ---- 截图预览区 ----
        preview_label = QLabel("截图预览")
        preview_label.setObjectName("section")
        main_layout.addWidget(preview_label)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setMaximumHeight(160)
        self._scroll.setMinimumHeight(80)

        self._preview_widget = QLabel("（无截图）")
        self._preview_widget.setAlignment(Qt.AlignCenter)
        self._preview_widget.setMinimumHeight(70)
        self._preview_widget.setStyleSheet(f"background-color: {COLOR_PREVIEW_BG}; color: {COLOR_TEXT_SUB};")
        self._scroll.setWidget(self._preview_widget)
        main_layout.addWidget(self._scroll)

        # ---- OCR 识别文字 ----
        ocr_header = QHBoxLayout()
        ocr_label = QLabel("识别文字")
        ocr_label.setObjectName("section")
        ocr_header.addWidget(ocr_label)
        ocr_header.addStretch()

        self.btn_copy_ocr = QPushButton("复制原文")
        self.btn_copy_ocr.setFixedHeight(38)
        self.btn_copy_ocr.setFixedWidth(110)
        self.btn_copy_ocr.clicked.connect(self._on_copy_ocr)
        ocr_header.addWidget(self.btn_copy_ocr)
        main_layout.addLayout(ocr_header)

        self.ocr_text = QTextEdit()
        self.ocr_text.setPlaceholderText("OCR 识别结果将显示在这里，可直接编辑...")
        self.ocr_text.setMaximumHeight(120)
        main_layout.addWidget(self.ocr_text)

        # ---- 翻译区域 ----
        trans_header = QHBoxLayout()
        trans_label = QLabel("翻译结果")
        trans_label.setObjectName("section")
        trans_header.addWidget(trans_label)
        trans_header.addStretch()

        # 语言选择
        self.lang_combo = QComboBox()
        self.lang_combo.setFixedHeight(38)
        for code, name in Translator.LANGUAGES.items():
            if code != "auto":
                self.lang_combo.addItem(name, code)
        self.lang_combo.setCurrentText("中文简体")
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        trans_header.addWidget(self.lang_combo)

        self.btn_translate = QPushButton("翻译")
        self.btn_translate.setObjectName("primary")
        self.btn_translate.setFixedHeight(38)
        self.btn_translate.setFixedWidth(100)
        self.btn_translate.clicked.connect(self._on_translate)
        trans_header.addWidget(self.btn_translate)
        main_layout.addLayout(trans_header)

        self.trans_text = QTextEdit()
        self.trans_text.setReadOnly(True)
        self.trans_text.setPlaceholderText("翻译结果将显示在这里...")
        self.trans_text.setMaximumHeight(120)
        main_layout.addWidget(self.trans_text)

        # ---- 底部按钮栏 ----
        bottom_layout = QHBoxLayout()

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 12px;")
        bottom_layout.addWidget(self._status_label)

        bottom_layout.addStretch()

        self.btn_copy_trans = QPushButton("复制译文")
        self.btn_copy_trans.setFixedHeight(38)
        self.btn_copy_trans.setFixedWidth(120)
        self.btn_copy_trans.clicked.connect(self._on_copy_trans)
        bottom_layout.addWidget(self.btn_copy_trans)

        self.btn_close = QPushButton("关闭")
        self.btn_close.setObjectName("primary")
        self.btn_close.setFixedHeight(38)
        self.btn_close.setFixedWidth(110)
        self.btn_close.clicked.connect(self.close)
        bottom_layout.addWidget(self.btn_close)

        main_layout.addLayout(bottom_layout)

    def set_screenshot(self, pil_img: Image.Image):
        """设置截图预览"""
        self._pil_img = pil_img
        if pil_img is None:
            return
        # PIL -> QPixmap
        buf = BytesIO()
        pil_img.save(buf, format="PNG")
        qimg = QImage()
        qimg.loadFromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimg)

        # 等比缩放到预览区域
        max_w = max(self._scroll.width() - 20, 300)
        max_h = self._scroll.maximumHeight() - 10
        scaled = pixmap.scaled(
            max_w, max_h,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._preview_widget.setPixmap(scaled)
        self._preview_widget.setAlignment(Qt.AlignCenter)

    def set_ocr_text(self, text: str):
        """设置 OCR 识别结果，并自动翻译"""
        self.ocr_text.setPlainText(text)
        self.trans_text.clear()
        # 有文字时自动翻译
        if text and text.strip():
            QTimer.singleShot(100, self._on_translate)

    def _on_translate(self):
        """点击翻译（异步，不阻塞 UI）"""
        text = self.ocr_text.toPlainText().strip()
        if not text:
            return
        target = self.lang_combo.currentData()
        self.translator.set_target_lang(target)
        self.btn_translate.setText("翻译中...")
        self.btn_translate.setEnabled(False)

        # 终止上一次未完成的翻译
        if self._worker and self._worker.isRunning():
            self._worker.quit()

        self._worker = TranslateWorker(self.translator, text)
        self._worker.finished.connect(self._on_translate_done)
        self._worker.start()

    def _on_translate_done(self, result: str):
        """翻译完成回调"""
        self.trans_text.setPlainText(result)
        self.btn_translate.setText("翻译")
        self.btn_translate.setEnabled(True)

    def _on_lang_changed(self):
        """切换语言时自动重新翻译"""
        text = self.ocr_text.toPlainText().strip()
        if text:
            QTimer.singleShot(100, self._on_translate)

    def _on_copy_ocr(self):
        """复制原文到剪贴板"""
        text = self.ocr_text.toPlainText()
        if text:
            copy_text_to_clipboard(text)
            self._flash_button(self.btn_copy_ocr, "已复制!")

    def _on_copy_trans(self):
        """复制译文到剪贴板"""
        text = self.trans_text.toPlainText()
        if text:
            copy_text_to_clipboard(text)
            self._flash_button(self.btn_copy_trans, "已复制!")

    def _flash_button(self, btn: QPushButton, text: str):
        """按钮点击反馈：2秒后恢复"""
        original = btn.text()
        btn.setText(text)
        btn.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: bold;")
        QTimer.singleShot(2000, lambda: (
            btn.setText(original),
            btn.setStyleSheet("")
        ))
