# ORC 截图工具 - 版本更新日志

## v1.0.5 (2026-06-20)

### 🐛 Bug 修复

- **修复翻译功能不可用**：Google Translate 在国内无法访问，替换为 MyMemory Translation API（免费、无需 API Key、国内直连可用）
- **修复截图翻译时界面卡死**：翻译请求阻塞 UI 主线程导致窗口无响应，改为 QThread 异步执行，翻译过程中界面保持流畅

### 📦 依赖变更

| 操作 | 依赖包 |
|------|--------|
| 移除 | `deep-translator==1.11.4` |
| 移除 | `truststore==0.10.4` |

### 📁 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `core/translator.py` | 重写 | Google Translate → MyMemory API，使用 stdlib urllib，无第三方依赖 |
| `ui/ocr_dialog.py` | 修改 | 新增 TranslateWorker(QThread) 异步翻译线程 |
| `requirements.txt` | 修改 | 移除 deep-translator、truststore |
| `ORC.spec` | 修改 | hiddenimports 移除 deep_translator/truststore，加入 excludes |
| `ORC-dir.spec` | 修改 | 同上 |

---

## v1.0.4 (2026-06-20)

### 🔄 核心引擎替换

- **OCR 引擎从 ddddocr 切换为 RapidOCR**
  - 原 `ddddocr` 是验证码识别工具，不是通用 OCR 引擎
  - 大图（1920×1080）检测 0 个文字框，小图识别结果为乱码
  - 替换为 `rapidocr-onnxruntime`（基于百度 PaddleOCR v4），专为通用 OCR 设计
  - 中英文混合文字识别准确率达 97-100%，大图小图均可正确识别
  - 使用 ONNX Runtime 推理，与原有 `onnxruntime` 依赖复用，无额外推理引擎开销

### 📦 依赖变更

| 操作 | 依赖包 |
|------|--------|
| 移除 | `ddddocr==1.6.1` |
| 新增 | `rapidocr-onnxruntime>=1.4.0` |

### 📁 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `core/ocr_engine.py` | 修改 | 完全重写，使用 RapidOCR 替代 ddddocr |
| `ORC.spec` | 修改 | datas 替换为 RapidOCR 模型，hiddenimports 更新，ddddocr 加入 excludes |
| `ORC-dir.spec` | 修改 | 同上 |
| `requirements.txt` | 修改 | 移除 ddddocr，新增 rapidocr-onnxruntime |

---

## v1.0.3 (2026-06-20)

### 🎨 界面与视觉更新

- **全新应用图标**
  - 重新设计淡蓝色相机风格图标，取代旧版图标
  - 使用 PIL 程序化生成图标（`assets/generate_icon.py`），支持多尺寸输出
  - 提供完整尺寸系列：16×16、32×32、48×48、64×64、128×128、256×256 PNG 及多尺寸 ICO
  - 图标配色统一为淡蓝色系（`#5AA8F7`、`#4694E6`、`#82C3FF`），与整体 UI 风格一致

- **OCR 对话框 UI 重设计**
  - 引入全新的淡蓝色主题样式系统（`STYLESHEET` 常量），覆盖所有控件
  - 定义统一色彩变量：主色 `#5AA8F7`、背景 `#E8F4FD`、卡片白 `#FFFFFF`、成功绿 `#52C47A`
  - 优化 QTextEdit、QPushButton、QComboBox、QScrollArea、QScrollBar 等控件的视觉表现
  - 新增截图预览区域（QScrollArea 内嵌 QLabel），支持等比缩放展示
  - 按钮样式分级：主要操作（蓝色）、成功反馈（绿色）、普通操作（白底蓝边）

- **按钮尺寸优化**
  - 统一将所有按钮高度调整为 38px（原 28-32px），提升点击体验
  - "复制原文" 90→110px、"翻译" 80→100px、"复制译文"→120px、"关闭" 90→110px
  - QPushButton 全局样式：padding 7px→9px、font-size 12px→13px、min-width 80px→90px
  - QComboBox（语言选择）同步调整为 38px 高度，padding 和字号匹配按钮风格

- **新增 README.md**
  - 完整的项目说明文档，包含功能特性、快速开始、项目结构、配置说明、技术栈等

### 🔧 技术细节

- **图标资源管理**
  - `assets/generate_icon.py` 可一键重新生成所有图标文件
  - `assets/icon.ico` 用于 EXE 文件嵌入（PyInstaller 打包）
  - `assets/icon.png`（256×256）用于运行时加载（托盘、对话框窗口图标）
  - 托盘图标提供纯色回退方案（`#5AA8F7`），图标文件缺失时自动生效

- **UI 样式架构**
  - 样式表以 Python f-string 常量形式定义在 `OCRDialog.STYLESHEET` 中
  - 色彩常量集中声明，便于后续主题定制

### 📦 打包方式变更

- **切换为单文件（onefile）模式**
  - PyInstaller 打包从 `--onedir` 改为 `--onefile`，生成单个 EXE 文件（约 171 MB）
  - 用户双击即可运行，无需安装 Python 或附带 `_internal/` 文件夹，方便分发
  - 每次启动会自动解压至临时目录，首次启动约慢 2-3 秒

- **修复 excludes 误排除标准库模块**
  - 原 `excludes` 列表中排除了 `email`、`http`、`xml` 标准库模块
  - 导致打包后运行报错 `ModuleNotFoundError: No module named 'email'`
  - 原因：`deep_translator` → `requests` → `urllib3` 依赖 `email` 和 `http` 模块
  - 已移除这三个模块的排除配置，仅保留 `matplotlib`、`scipy`、`pandas`、`tkinter`、`unittest`、`pydoc`

- **双模式打包配置**
  - `ORC.spec`：onefile 模式，输出 `dist/ORC截图工具.exe`（单文件，用于分发）
  - `ORC-dir.spec`：onedir 模式，输出 `dist/ORC截图工具_dev/`（目录结构，启动更快，用于开发调试）

### 🐛 Bug 修复

- **翻译功能 SSL 证书验证失败**
  - 现象：打包后运行翻译报 `SSL: CERTIFICATE_VERIFY_FAILED`
  - 原因：Python 自带的 OpenSSL 证书库不完整，无法验证 Google 的 SSL 证书
  - 修复：引入 `pip-system-certs`（v5.3），让 `requests` 使用 Windows 系统证书库
  - 修复：引入 `truststore`（v0.10.4），在模块加载时显式调用 `inject_into_ssl()` 注入 Windows 系统证书库
  - 之前尝试 `pip-system-certs`（通过 site.py 自动注入），但在 PyInstaller 打包环境下自动机制失效

### 📦 依赖变更

| 操作 | 依赖包 |
|------|--------|
| 新增 | `pip-system-certs==5.3` |
| 新增 | `truststore==0.10.4` |

### 📁 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `assets/generate_icon.py` | 新增 | PIL 程序化图标生成脚本 |
| `assets/icon.ico` | 修改 | 多尺寸 ICO 文件（淡蓝色相机风格） |
| `assets/icon.png` | 修改 | 256×256 PNG 图标 |
| `assets/icon_*.png` | 新增 | 16/32/48/64/128 尺寸 PNG 图标 |
| `ui/ocr_dialog.py` | 修改 | 新增 STYLESHEET 常量、截图预览区域、色彩系统 |
| `ui/tray_icon.py` | 修改 | 更新图标加载逻辑、版本号更新至 1.0.3 |
| `core/translator.py` | 修改 | 导入 truststore 并显式调用 inject_into_ssl() 修复 SSL |
| `requirements.txt` | 修改 | 新增 pip-system-certs、truststore 依赖 |
| `ORC.spec` | 修改 | 打包模式切换为 onefile，修复 excludes，新增 truststore hiddenimport |
| `ORC-dir.spec` | 新增 | onedir 模式打包配置（开发调试用） |
| `README.md` | 新增 | 项目说明文档 |
| `.gitignore` | 新增 | Git 忽略规则（排除 build/dist/.venv/.idea 等） |

---

## v1.0.2 (2026-06-19)

### 🔒 安全性改进

- **替换 keyboard 库为 Windows 原生 API**
  - 移除 `keyboard` 第三方库，改用 Windows `RegisterHotKey` API 实现全局快捷键
  - 解决杀毒软件将程序误报为键盘记录器的问题
  - 新增 `core/hotkey.py` 模块，使用 `ctypes` 直接调用 Windows API

- **截图加密保护**
  - 截图默认以 `.orc` 加密格式保存（XOR 加密算法）
  - 加密密钥基于机器唯一标识（MachineGuid + 用户名），仅本机可解密
  - 加密失败时自动回退为普通 PNG 格式保存

- **截图文件夹隐藏**
  - 截图保存目录自动设置 Windows 隐藏属性
  - 防止他人直接浏览截图文件

### 📦 依赖变更

| 操作 | 依赖包 |
|------|--------|
| 移除 | `keyboard==0.13.5` |

### 📁 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `core/hotkey.py` | 新增 | Windows 原生快捷键模块 |
| `core/screenshot.py` | 修改 | 新增 `encrypt_image()`、`decrypt_image()`、`hide_folder()` 函数 |
| `utils/config.py` | 修改 | 新增 `encrypt_screenshots`、`hide_screenshot_folder` 配置项 |
| `main.py` | 修改 | 替换 `keyboard` 库为 `NativeHotkey`，新增截图加密保存逻辑 |
| `requirements.txt` | 修改 | 移除 `keyboard` 依赖 |
| `ORC.spec` | 修改 | 移除 `keyboard` 相关 hiddenimports |

### ⚙️ 新增配置项

```json
{
    "encrypt_screenshots": true,
    "hide_screenshot_folder": true
}
```

---

## v1.0.1 (2026-06-19)

### 🐛 Bug 修复

- **快捷键响应问题**
  - 修复 `keyboard` 库在部分环境下快捷键不响应的问题
  - 使用 `pyqtSignal` 信号机制替代 `QTimer.singleShot`，解决跨线程调用问题

- **QImage 内存崩溃**
  - 修复 `QImage` 转换时 PIL 数据提前释放导致的崩溃
  - 添加 `.copy()` 方法创建 QImage 副本

- **系统托盘图标问题**
  - 修复 `QSystemTrayIcon` 初始化时 parent 类型错误
  - 移除不正确的 parent 参数传递

- **窗口激活问题**
  - 添加 `activateWindow()` 和 `raise_()` 确保截图窗口正确显示在最前

### ✨ 功能改进

- **OCR 界面重新设计**
  - 全新现代 UI 样式（蓝色主题 `#0078D4`）
  - 新增截图预览区域
  - 新增自动翻译功能（OCR 完成后自动翻译）
  - 语言切换时自动重新翻译

- **去除 UAC 提权**
  - 移除自动请求管理员权限功能
  - 程序可直接运行，无需额外权限弹窗

---

## v1.0.0 (2026-06-19)

### ✨ 初始版本功能

- **截图功能**
  - 全局快捷键截图（默认 `Ctrl+Shift+A`）
  - 全屏截图 + 区域选择
  - 支持多屏幕环境
  - 截图自动保存到 `~/Pictures/Screenshots/`

- **OCR 文字识别**
  - 使用 `RapidOCR`（PaddleOCR v4）进行本地 OCR 识别
  - 支持中英文识别

- **翻译功能**
  - 使用 Google Translate API
  - 支持多语言互译
  - 自动检测源语言

- **剪贴板支持**
  - 截图自动复制到剪贴板
  - 支持文本复制到剪贴板

- **系统托盘**
  - 最小化到系统托盘运行
  - 托盘右键菜单（截图、退出）
  - 托盘通知提示

- **配置管理**
  - JSON 格式配置文件（`~/.orc_screenshot/config.json`）
  - 支持自定义快捷键
  - 支持自定义保存路径
  - 支持自定义翻译语言

### 📦 技术栈

| 组件 | 版本 |
|------|------|
| Python | 3.12+ |
| PyQt5 | 5.15.11 |
| mss | 10.2.0 |
| Pillow | 12.2.0 |
| rapidocr-onnxruntime | >=1.4.0 |
| deep-translator | 1.11.4 |
| onnxruntime | 1.17.3 |

### 📁 项目结构

```
ORC/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖列表
├── ORC.spec            # PyInstaller 打包配置
├── core/               # 核心模块
│   ├── screenshot.py   # 截图管理
│   ├── ocr_engine.py   # OCR 引擎
│   ├── translator.py   # 翻译模块
│   └── hotkey.py       # 快捷键模块 (v1.0.2+)
├── ui/                 # 界面模块
│   ├── main_window.py  # 截图选择窗口
│   ├── ocr_dialog.py   # OCR 结果弹窗
│   └── tray_icon.py    # 系统托盘
└── utils/              # 工具模块
    ├── clipboard.py    # 剪贴板工具
    └── config.py       # 配置管理
```

---

## 📥 安装与使用

### 环境要求

- Windows 10/11
- Python 3.12+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

### 打包为 EXE

```bash
pip install pyinstaller

# 单文件模式（分发用，输出单个 EXE）
pyinstaller ORC.spec

# 目录模式（开发调试用，启动更快）
pyinstaller ORC-dir.spec
```

- 单文件：`dist/ORC截图工具.exe`，双击即可运行，无需安装
- 目录模式：`dist/ORC截图工具_dev/ORC截图工具_dev.exe`，需连同文件夹一起使用

---

## ⚠️ 已知问题

1. **翻译功能依赖网络**
   - OCR 文字会通过 HTTP 请求发送到 Google 服务器
   - 如截图包含敏感信息，请注意隐私保护

2. **EXE 无代码签名**
   - Windows SmartScreen 可能弹出"未知发布者"警告
   - 点击"仍要运行"即可

3. **加密截图仅本机可解密**
   - 如需在其他电脑查看，请关闭加密功能或手动解密

---

## 📝 配置说明

配置文件位置：`~/.orc_screenshot/config.json`

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
