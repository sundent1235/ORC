"""
翻译模块
使用 MyMemory Translation API（免费，无需 API Key，国内可用）
文档：https://mymemory.translated.net/doc/spec.php
"""
import urllib.request
import urllib.parse
import json


class Translator:
    """翻译器 — MyMemory API"""

    # 支持的语言列表
    LANGUAGES = {
        "auto": "自动检测",
        "zh-CN": "中文简体",
        "en": "英语",
        "ja": "日语",
        "ko": "韩语",
        "fr": "法语",
        "de": "德语",
        "es": "西班牙语",
        "ru": "俄语",
    }

    # MyMemory 语言代码映射
    _LANG_MAP = {
        "auto": "auto",
        "zh-CN": "zh-CN",
        "en": "en",
        "ja": "ja",
        "ko": "ko",
        "fr": "fr",
        "de": "de",
        "es": "es",
        "ru": "ru",
    }

    def __init__(self, source_lang: str = "auto", target_lang: str = "zh-CN"):
        self.source_lang = source_lang
        self.target_lang = target_lang

    def set_source_lang(self, lang: str):
        """设置源语言"""
        self.source_lang = lang

    def set_target_lang(self, lang: str):
        """设置目标语言"""
        self.target_lang = lang

    def translate(self, text: str) -> str:
        """
        翻译文本
        :param text: 待翻译的文字
        :return: 翻译结果
        """
        if not text or not text.strip():
            return ""

        try:
            source = self._LANG_MAP.get(self.source_lang, "en")
            target = self._LANG_MAP.get(self.target_lang, "zh-CN")

            # 自动检测源语言时，默认英语（最常见的 OCR 外语）
            if source == "auto":
                source = "en"

            langpair = f"{source}|{target}"

            params = urllib.parse.urlencode({
                "q": text,
                "langpair": langpair,
            })
            url = f"https://api.mymemory.translated.net/get?{params}"

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "ORC-Screenshot-Tool/1.0.4",
                },
            )

            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            status = result.get("responseStatus")
            if status == 200:
                translated = result.get("responseData", {}).get("translatedText", "")
                # MyMemory 有时返回全大写，尝试修正
                matches = result.get("matches", [])
                for match in matches:
                    if match.get("translation") and match.get("quality", "0") != "0":
                        translated = match["translation"]
                        break
                return translated.strip()
            else:
                detail = result.get("responseDetails", "")
                return f"[翻译出错] {status}: {detail}"

        except urllib.error.URLError as e:
            return f"[翻译出错] 网络错误: {e.reason}"
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
