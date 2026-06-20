# -*- mode: python ; coding: utf-8 -*-
"""
ORC 截图工具 PyInstaller 打包配置
使用方法：pyinstaller ORC.spec
"""
import os
import sys

# 项目根目录
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))

# rapidocr 包路径（模型文件 + 配置）
RAPIDOCR_DIR = os.path.join(sys.prefix, 'Lib', 'site-packages', 'rapidocr_onnxruntime')
if not os.path.exists(RAPIDOCR_DIR):
    import importlib.util
    spec = importlib.util.find_spec('rapidocr_onnxruntime')
    if spec:
        RAPIDOCR_DIR = os.path.dirname(spec.origin)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        # rapidocr ONNX 模型 + 配置（必须打包）
        (os.path.join(RAPIDOCR_DIR, 'config.yaml'), 'rapidocr_onnxruntime'),
        (os.path.join(RAPIDOCR_DIR, 'models', 'ch_PP-OCRv4_det_infer.onnx'),
         os.path.join('rapidocr_onnxruntime', 'models')),
        (os.path.join(RAPIDOCR_DIR, 'models', 'ch_PP-OCRv4_rec_infer.onnx'),
         os.path.join('rapidocr_onnxruntime', 'models')),
        (os.path.join(RAPIDOCR_DIR, 'models', 'ch_ppocr_mobile_v2.0_cls_infer.onnx'),
         os.path.join('rapidocr_onnxruntime', 'models')),
        # 图标资源
        (os.path.join(PROJECT_DIR, 'assets', 'icon.png'), 'assets'),
    ],
    hiddenimports=[
        'mss',
        'mss.windows',
        'rapidocr_onnxruntime',
        'onnxruntime',
        'onnxruntime.capi',
        'onnxruntime.capi._pybind_state',
        'PIL',
        'PIL._imaging',
        'cv2',
        'numpy',
        'yaml',
        'shapely',
        'pyclipper',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
        'unittest',
        'pydoc',
        'ddddocr',
        'deep_translator',
        'truststore',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ORC截图工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               # 不显示控制台窗口（GUI 程序）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_DIR, 'assets', 'icon.ico'),   # EXE 图标
)
