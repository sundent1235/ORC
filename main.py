"""ORC 截图工具 - 主程序入口
功能：截图、OCR文字识别、翻译、剪贴板
快捷键：Ctrl+Shift+A 截图
"""
import sys
import os
from datetime import datetime

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QObject, pyqtSignal

from core.screenshot import ScreenshotManager, encrypt_image, hide_folder
from core.ocr_engine import OCREngine
from core.translator import Translator
from core.hotkey import NativeHotkey
from utils.clipboard import copy_image_to_clipboard
from utils.config import Config
from ui.main_window import ScreenshotWindow
from ui.ocr_dialog import OCRDialog
from ui.tray_icon import TrayIcon


class SignalBridge(QObject):
    """跨线程信号桥"""
    start_screenshot_signal = pyqtSignal()


class ORCApp:
    """主应用控制器"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出（托盘运行）

        self.config = Config()
        self.screenshot_mgr = ScreenshotManager()
        self.ocr_engine = OCREngine()
        self.translator = Translator(
            source_lang=self.config.source_lang,
            target_lang=self.config.target_lang
        )

        self.screenshot_window = None
        self.ocr_dialog = None
        self.tray_icon = None
        self.hotkey = None
        self.signal_bridge = SignalBridge()
        self.signal_bridge.start_screenshot_signal.connect(self.start_screenshot)

        self._init_tray()
        self._register_hotkeys()

    def _init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = TrayIcon()
        self.tray_icon.screenshot_triggered.connect(self.start_screenshot)
        self.tray_icon.quit_triggered.connect(self.quit)
        self.tray_icon.show()

    def _register_hotkeys(self):
        """注册全局快捷键（使用 Windows 原生 API）"""
        hotkey_str = self.config.hotkey_screenshot
        try:
            self.hotkey = NativeHotkey(hotkey_str)
            self.hotkey.triggered.connect(self._on_hotkey_screenshot)
            self.hotkey.register()
        except Exception as e:
            print(f"[警告] 快捷键 {hotkey_str} 注册失败: {e}")

    def _on_hotkey_screenshot(self):
        """快捷键触发截图"""
        print("[快捷键] 检测到截图快捷键!")
        self.signal_bridge.start_screenshot_signal.emit()

    def start_screenshot(self):
        """开始截图流程"""
        print("[截图] 开始截取全屏...")
        try:
            # 先截取全屏（作为背景）
            full_img = self.screenshot_mgr.capture_full_screen()
            print(f"[截图] 全屏截图完成: {full_img.size}, 模式: {full_img.mode}")

            # PIL Image -> QPixmap（copy 避免内存提前释放）
            img_bytes = full_img.tobytes()
            qimage = QImage(
                img_bytes,
                full_img.width,
                full_img.height,
                full_img.width * 3,
                QImage.Format_RGB888
            ).copy()  # 复制一份，避免 PIL 数据释放后 QImage 崩溃
            pixmap = QPixmap.fromImage(qimage)
            print(f"[截图] QPixmap 创建完成: {pixmap.size()}")

            # 打开截图选择窗口
            self.screenshot_window = ScreenshotWindow(pixmap)
            self.screenshot_window.screenshot_taken.connect(self._on_screenshot_done)
            self.screenshot_window.screenshot_cancelled.connect(self._on_screenshot_cancel)
            self.screenshot_window.show()
            print("[截图] 截图选择窗口已打开")
        except Exception as e:
            print(f"[截图] 截图失败: {e}")
            import traceback
            traceback.print_exc()

    def _on_screenshot_done(self, pil_img):
        """截图完成回调"""
        # 自动复制到剪贴板（加密不影响剪贴板）
        if self.config.get("auto_copy_clipboard", True):
            try:
                copy_image_to_clipboard(pil_img)
                self.tray_icon.show_message("截图完成", "图片已复制到剪贴板")
            except Exception:
                pass

        # 保存到文件（支持加密）
        save_dir = self.config.save_dir
        os.makedirs(save_dir, exist_ok=True)

        # 隐藏截图文件夹
        if self.config.get("hide_screenshot_folder", True):
            hide_folder(save_dir)

        # 加密或普通保存
        encrypt = self.config.get("encrypt_screenshots", True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if encrypt:
            filepath = os.path.join(save_dir, ts + ".orc")
            try:
                enc_data = encrypt_image(pil_img)
                with open(filepath, "wb") as f:
                    f.write(enc_data)
                print(f"[截图] 加密保存: {filepath}")
            except Exception as e:
                # 加密失败则回退到普通保存
                filepath = os.path.join(save_dir, ts + ".png")
                self.screenshot_mgr.save_to_file(pil_img, filepath)
                print(f"[截图] 加密失败，普通保存: {filepath} ({e})")
        else:
            filepath = os.path.join(save_dir, ts + ".png")
            self.screenshot_mgr.save_to_file(pil_img, filepath)
            print(f"[截图] 普通保存: {filepath}")

        # 执行 OCR
        try:
            ocr_text = self.ocr_engine.recognize_text(pil_img)
        except Exception as e:
            ocr_text = f"[OCR 识别出错] {str(e)}"

        # 显示 OCR 结果弹窗
        self.ocr_dialog = OCRDialog()
        self.ocr_dialog.set_screenshot(pil_img)
        self.ocr_dialog.set_ocr_text(ocr_text)
        self.ocr_dialog.show()

    def _on_screenshot_cancel(self):
        """截图取消回调"""
        pass

    def quit(self):
        """退出程序"""
        if self.hotkey:
            self.hotkey.unregister()
        self.screenshot_mgr.close()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """启动应用"""
        print("ORC 截图工具已启动！")
        print(f"截图快捷键: {self.config.hotkey_screenshot}")
        sys.exit(self.app.exec_())


def main():
    app = ORCApp()
    app.run()


if __name__ == "__main__":
    main()
