"""
翻译模块
使用 deep-translator 支持 Google 翻译（免费）
"""
import ssl as _ssl

import truststore as _truststore  # 使用 Windows 系统证书库，修复 SSL 验证
if not isinstance(_ssl.create_default_context(), _truststore.SSLContext):
    _truststore.inject_into_ssl()

from deep_translator import GoogleTranslator


class Translator:
    """翻译器"""

    # 支持的语言列表
    LANGUAGES = {
        "auto": "自动检测",
        "zh-CN": "中文简体",
        "zh-TW": "中文繁体",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
    }

    def __init__(self, source_lang: str = "auto", target_lang: str = "zh-CN"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self._translator = None

    @property
    def translator(self):
        if self._translator is None:
            self._update_translator()
        return self._translator

    def _update_translator(self):
        src = "auto" if self.source_lang == "auto" else self.source_lang
        self._translator = GoogleTranslator(source=src, target=self.target_lang)

    def set_source_lang(self, lang: str):
        """设置源语言"""
        self.source_lang = lang
        self._translator = None

    def set_target_lang(self, lang: str):
        """设置目标语言"""
        self.target_lang = lang
        self._translator = None

    def translate(self, text: str) -> str:
        """
        翻译文本
        :param text: 待翻译的文字
        :return: 翻译结果
        """
        if not text or not text.strip():
            return ""

        try:
            result = self.translator.translate(text)
            return result if result else ""
        except Exception as e:
            return f"[翻译出错] {str(e)}"

    def translate_batch(self, texts: list) -> list:
        """批量翻译"""
        results = []
        for text in texts:
            results.append(self.translate(text))
        return results

    @staticmethod
    def get_supported_languages() -> dict:
        """获取支持的语言列表"""
        return Translator.LANGUAGES
