"""
配置管理模块
管理快捷键、保存路径、语言等配置
"""
import json
import os

# 默认配置文件路径
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".orc_screenshot")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# 默认配置
DEFAULT_CONFIG = {
    "hotkey_screenshot": "ctrl+shift+a",   # 截图快捷键
    "hotkey_ocr": "ctrl+shift+o",           # OCR 快捷键
    "save_dir": os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots"),
    "source_lang": "auto",
    "target_lang": "zh-CN",
    "auto_copy_clipboard": True,            # 截图后自动复制到剪贴板
    "image_format": "PNG",
    "show_tray": True,                      # 显示系统托盘
    "encrypt_screenshots": True,            # 加密保存截图（仅本机可解密）
    "hide_screenshot_folder": True,         # 隐藏截图文件夹
}


class Config:
    """配置管理器"""

    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _ensure_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

    def _load(self):
        """从文件加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._config.update(data)
            except Exception:
                pass  # 文件损坏则用默认配置

    def save(self):
        """保存配置到文件"""
        self._ensure_dir()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value):
        """设置配置值并保存"""
        self._config[key] = value
        self.save()

    def reset(self):
        """重置为默认配置"""
        self._config = DEFAULT_CONFIG.copy()
        self.save()

    @property
    def save_dir(self) -> str:
        return self._config.get("save_dir", DEFAULT_CONFIG["save_dir"])

    @property
    def hotkey_screenshot(self) -> str:
        return self._config.get("hotkey_screenshot", "ctrl+shift+a")

    @property
    def source_lang(self) -> str:
        return self._config.get("source_lang", "auto")

    @property
    def target_lang(self) -> str:
        return self._config.get("target_lang", "zh-CN")
