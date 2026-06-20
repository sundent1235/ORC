# ORC 截图工具

一款轻量级 Windows 桌面截图工具，集成 OCR 文字识别和多语言翻译功能。截图后自动识别图中文字并翻译，适合阅读外文界面、文档、代码注释等场景。

## 功能特性

- **快捷键截图** — 全局快捷键 `Ctrl+Shift+A`，支持全屏截图和区域选择，支持多显示器
- **本地 OCR 识别** — 基于 RapidOCR（PaddleOCR v4）引擎，无需联网即可识别中英文文字
- **自动翻译** — OCR 完成后自动调用 Google Translate 翻译，支持中/英/日/韩/法/德/西/俄等语言
- **截图加密** — 截图以 XOR 加密格式保存，密钥绑定本机，防止他人直接查看
- **剪贴板集成** — 截图自动复制到剪贴板，OCR 文字和翻译结果一键复制
- **系统托盘** — 最小化到托盘运行，不占用任务栏空间

## 环境要求

- Windows 10 / 11
- Python 3.12+（从源码运行时需要）

## 快速开始

### 使用打包好的 EXE（推荐）

直接双击 `ORC截图工具.exe` 即可运行，无需安装 Python 环境。

> 首次运行时 Windows SmartScreen 可能提示"未知发布者"，点击"更多信息" → "仍要运行"即可。

### 从源码运行

```bash
# 克隆项目
git clone <仓库地址>
cd ORC

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

### 自行打包为 EXE

```bash
pip install pyinstaller

# 单文件模式（分发用，输出单个 EXE）
pyinstaller ORC.spec

# 目录模式（开发调试用，启动更快）
pyinstaller ORC-dir.spec
```

- 单文件：`dist/ORC截图工具.exe`
- 目录模式：`dist/ORC截图工具_dev/ORC截图工具_dev.exe`

## 项目结构

```
ORC/
├── main.py               # 主程序入口
├── requirements.txt       # 依赖列表
├── ORC.spec              # PyInstaller 单文件打包配置
├── ORC-dir.spec          # PyInstaller 目录模式打包配置
├── assets/               # 图标资源
│   ├── generate_icon.py  # 图标生成脚本（PIL）
│   ├── icon.ico          # 多尺寸 ICO（EXE 嵌入用）
│   └── icon.png          # 256×256 PNG（运行时加载）
├── core/                 # 核心模块
│   ├── hotkey.py         # Windows 原生快捷键（RegisterHotKey API）
│   ├── ocr_engine.py     # RapidOCR (PaddleOCR v4) OCR 引擎
│   ├── screenshot.py     # 截图管理 + XOR 加密
│   └── translator.py     # Google Translate 翻译模块
├── ui/                   # 界面模块
│   ├── main_window.py    # 截图区域选择窗口
│   ├── ocr_dialog.py     # OCR 结果弹窗（截图预览 + 识别 + 翻译）
│   └── tray_icon.py      # 系统托盘图标 + 右键菜单
└── utils/                # 工具模块
    ├── clipboard.py      # 剪贴板操作
    └── config.py         # JSON 配置管理
```

## 配置说明

配置文件位于 `~/.orc_screenshot/config.json`，首次运行自动创建：

```json
{
    "hotkey_screenshot": "ctrl+shift+a",
    "save_dir": "~/Pictures/Screenshots",
    "source_lang": "auto",
    "target_lang": "zh-CN",
    "auto_copy_clipboard": true,
    "image_format": "PNG",
    "show_tray": true,
    "encrypt_screenshots": true,
    "hide_screenshot_folder": true
}
```

## 技术栈

| 组件 | 用途 |
|------|------|
| PyQt5 | GUI 框架 |
| mss | 屏幕截图 |
| RapidOCR (PaddleOCR v4) | 本地 OCR 识别 |
| deep-translator | Google Translate API |
| Pillow | 图片处理 |
| truststore | Windows 系统 SSL 证书 |
| PyInstaller | 打包为 EXE |

## 已知问题

- 翻译功能需要联网，OCR 文字会通过 HTTP 发送到 Google 服务器，如截图含敏感信息请注意隐私
- EXE 无代码签名，Windows SmartScreen 会弹出"未知发布者"警告
- 加密截图使用机器绑定密钥，仅本机可解密，换电脑需关闭加密或手动解密

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)
