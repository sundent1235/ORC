"""截图核心模块
支持全屏截图、区域截图、多屏幕截图
支持截图加密保护（仅本机可解密）
"""
import os
import ctypes
import hashlib
import winreg
import mss
from PIL import Image
from io import BytesIO


# 加密文件标识头（用于验证是否是本机加密的文件）
_ENC_MAGIC = b"ORC_ENC_V1"


def _get_machine_key() -> bytes:
    """生成机器唯一密钥（基于 MachineGuid + 用户名）
    同一台电脑始终生成相同的密钥，其他电脑无法解密
    """
    # 读取 Windows 机器唯一 ID
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        )
        machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        machine_guid = "fallback_guid"

    # 加上用户名作为盐值
    username = os.getlogin()
    raw = f"{machine_guid}:{username}:ORC_Screenshot"
    return hashlib.sha256(raw.encode("utf-8")).digest()


def _xor_crypt(data: bytes, key: bytes) -> bytes:
    """XOR 加密/解密（对称，同一操作即可加密和解密）"""
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def encrypt_image(img: Image.Image, fmt: str = "PNG") -> bytes:
    """将图片加密后返回字节
    格式: [ORC_ENC_V1][32字节密钥校验][加密后的图片数据]
    """
    key = _get_machine_key()
    buf = BytesIO()
    img.save(buf, format=fmt)
    img_bytes = buf.getvalue()

    # 密钥校验值（取 SHA256 的前 8 字节）
    key_check = hashlib.sha256(key).digest()[:8]

    # 加密图片数据
    encrypted = _xor_crypt(img_bytes, key)

    return _ENC_MAGIC + key_check + encrypted


def decrypt_image(data: bytes) -> Image.Image:
    """解密图片字节，返回 PIL Image
    如果不是加密文件，直接作为普通图片加载
    """
    if not data.startswith(_ENC_MAGIC):
        # 不是加密文件，直接加载
        return Image.open(BytesIO(data))

    key = _get_machine_key()
    key_check = hashlib.sha256(key).digest()[:8]

    # 读取文件中存储的校验值
    stored_check = data[len(_ENC_MAGIC):len(_ENC_MAGIC) + 8]
    if stored_check != key_check:
        raise ValueError("无法解密：此截图不是在本机加密的")

    # 取出加密的图片数据并解密
    encrypted_data = data[len(_ENC_MAGIC) + 8:]
    decrypted = _xor_crypt(encrypted_data, key)

    return Image.open(BytesIO(decrypted))


def hide_folder(folder_path: str):
    """设置 Windows 文件夹隐藏属性"""
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass


def unhide_folder(folder_path: str):
    """取消 Windows 文件夹隐藏属性"""
    try:
        FILE_ATTRIBUTE_NORMAL = 0x80
        ctypes.windll.kernel32.SetFileAttributesW(folder_path, FILE_ATTRIBUTE_NORMAL)
    except Exception:
        pass


class ScreenshotManager:
    """截图管理器"""

    def __init__(self):
        self._sct = None

    @property
    def sct(self):
        """延迟初始化 mss 实例（避免线程问题）"""
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct

    def capture_full_screen(self) -> Image.Image:
        """截取所有屏幕的全屏"""
        monitor = self.sct.monitors[0]  # 0 = 所有屏幕合并
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    def capture_monitor(self, monitor_index: int = 1) -> Image.Image:
        """截取指定屏幕（从1开始）"""
        if monitor_index >= len(self.sct.monitors):
            monitor_index = 1
        monitor = self.sct.monitors[monitor_index]
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """截取指定区域"""
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img

    @staticmethod
    def to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
        """将 PIL Image 转为字节流"""
        buffer = BytesIO()
        img.save(buffer, format=fmt)
        return buffer.getvalue()

    @staticmethod
    def save_to_file(img: Image.Image, filepath: str, fmt: str = "PNG"):
        """将截图保存到文件"""
        img.save(filepath, format=fmt)
        return filepath

    def get_monitors(self) -> list:
        """获取所有屏幕信息"""
        return self.sct.monitors

    def close(self):
        """关闭 mss 实例"""
        if self._sct is not None:
            self._sct.close()
            self._sct = None
