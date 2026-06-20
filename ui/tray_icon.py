"""
系统托盘图标模块
支持最小化到托盘、右键菜单
"""
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import pyqtSignal, QObject

# 图标路径（兼容 PyInstaller 打包）
import sys
if getattr(sys, 'frozen', False):
    _ASSETS_DIR = os.path.join(sys._MEIPASS, 'assets')
else:
    _ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
_ICON_PATH = os.path.join(_ASSETS_DIR, 'icon.png')


class TrayIcon(QObject):
    """系统托盘图标"""

    # 信号
    screenshot_triggered = pyqtSignal()   # 截图信号
    quit_triggered = pyqtSignal()          # 退出信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray = QSystemTrayIcon()
        self._init_icon()
        self._init_menu()

    def _init_icon(self):
        """创建托盘图标"""
        # 优先使用生成的图标文件
        if os.path.exists(_ICON_PATH):
            icon = QIcon(_ICON_PATH)
        else:
            # 回退：程序生成简单图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(90, 168, 247))
            icon = QIcon(pixmap)
        self.tray.setIcon(icon)
        self.tray.setToolTip("ORC 截图工具")
        self.tray.activated.connect(self._on_activated)

    def _init_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 截图按钮
        action_capture = QAction("截图 (Ctrl+Shift+A)", menu)
        action_capture.triggered.connect(self.screenshot_triggered.emit)
        menu.addAction(action_capture)

        menu.addSeparator()

        # 关于
        action_about = QAction("关于", menu)
        action_about.triggered.connect(self._show_about)
        menu.addAction(action_about)

        menu.addSeparator()

        # 退出
        action_quit = QAction("退出", menu)
        action_quit.triggered.connect(self.quit_triggered.emit)
        menu.addAction(action_quit)

        self.tray.setContextMenu(menu)

    def _on_activated(self, reason):
        """托盘图标点击事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.screenshot_triggered.emit()

    def _show_about(self):
        """显示关于信息"""
        self.tray.showMessage(
            "ORC 截图工具",
            "版本 1.0.5\n截图 / OCR / 翻译\n快捷键: Ctrl+Shift+A",
            QSystemTrayIcon.Information,
            3000
        )

    def show(self):
        """显示托盘图标"""
        self.tray.show()

    def hide(self):
        """隐藏托盘图标"""
        self.tray.hide()

    def show_message(self, title: str, message: str, duration: int = 2000):
        """显示气泡通知"""
        self.tray.showMessage(title, message, QSystemTrayIcon.Information, duration)
