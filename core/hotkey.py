"""
全局快捷键模块
使用 Windows 原生 RegisterHotKey API，无需 keyboard 库（避免被杀毒软件误报）
"""
import ctypes
import ctypes.wintypes as wintypes
import threading
from PyQt5.QtCore import QObject, pyqtSignal


# Windows 修饰键常量
MOD_ALT     = 0x0001
MOD_CTRL    = 0x0002
MOD_SHIFT   = 0x0004
MOD_WIN     = 0x0008

# Windows 消息常量
WM_HOTKEY   = 0x0312

# 修饰键名称映射
_MODIFIER_MAP = {
    "ctrl":    MOD_CTRL,
    "control": MOD_CTRL,
    "shift":   MOD_SHIFT,
    "alt":     MOD_ALT,
    "win":     MOD_WIN,
    "super":   MOD_WIN,
}

# 常用虚拟键码映射（不区分大小写）
_VK_MAP = {
    "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45, "f": 0x46,
    "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A, "k": 0x4B, "l": 0x4C,
    "m": 0x4D, "n": 0x4E, "o": 0x4F, "p": 0x50, "q": 0x51, "r": 0x52,
    "s": 0x53, "t": 0x54, "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58,
    "y": 0x59, "z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "space": 0x20, "enter": 0x0D, "tab": 0x09, "esc": 0x1B,
    "printscreen": 0x2C, "scrolllock": 0x91, "pause": 0x13,
}


def parse_hotkey(hotkey_str: str):
    """
    解析快捷键字符串，返回 (modifiers, vk_code)
    示例：'ctrl+shift+a' → (MOD_CTRL | MOD_SHIFT, 0x41)
    """
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    modifiers = 0
    key = None

    for part in parts:
        if part in _MODIFIER_MAP:
            modifiers |= _MODIFIER_MAP[part]
        elif part in _VK_MAP:
            key = _VK_MAP[part]

    if key is None:
        raise ValueError(f"无法解析快捷键: '{hotkey_str}'，请检查按键名称是否正确")

    return modifiers, key


class NativeHotkey(QObject):
    """
    原生 Windows 全局快捷键
    使用 RegisterHotKey API，不会被杀毒软件误报
    """

    triggered = pyqtSignal()   # 快捷键触发信号

    def __init__(self, hotkey_str: str, parent=None):
        super().__init__(parent)
        self.hotkey_str = hotkey_str
        self._modifiers, self._vk = parse_hotkey(hotkey_str)
        self._hotkey_id = 1
        self._thread = None
        self._running = False

    def register(self) -> bool:
        """注册全局快捷键（在后台线程运行）"""
        if self._running:
            return True

        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()
        return True

    def _listen(self):
        """后台线程：注册热键并等待触发"""
        user32 = ctypes.windll.user32

        # 注册全局热键（线程级，线程退出自动失效）
        success = user32.RegisterHotKey(None, self._hotkey_id, self._modifiers, self._vk)
        if not success:
            err = ctypes.windll.kernel32.GetLastError()
            print(f"[快捷键] 注册失败: '{self.hotkey_str}' (错误码: {err})")
            print("[快捷键] 可能该快捷键已被其他程序占用")
            self._running = False
            return

        print(f"[快捷键] 成功注册: '{self.hotkey_str}' (Windows 原生 API)")

        msg = wintypes.MSG()
        while self._running:
            # GetMessage 阻塞等待，CPU 占用极低
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0 or result == -1:
                break
            if msg.message == WM_HOTKEY and msg.wParam == self._hotkey_id:
                self.triggered.emit()

        # 线程退出时自动注销
        user32.UnregisterHotKey(None, self._hotkey_id)
        print(f"[快捷键] 已注销: '{self.hotkey_str}'")

    def unregister(self):
        """停止监听（触发线程退出）"""
        self._running = False
        # 发一条空消息让 GetMessageW 返回，从而退出循环
        if self._thread and self._thread.is_alive():
            try:
                user32 = ctypes.windll.user32
                user32.PostThreadMessageW(
                    self._thread.ident, 0x0012, 0, 0  # WM_QUIT
                )
            except Exception:
                pass
