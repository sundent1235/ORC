"""生成 ORC 截图工具的应用图标（淡蓝色相机风格）"""
from PIL import Image, ImageDraw
import os

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_icon(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 比例缩放
    s = size / 256

    def r(x, y, x2, y2):
        return [int(v * s) for v in (x, y, x2, y2)]

    # 外圆角矩形 - 深蓝边框
    d.rounded_rectangle(r(12, 12, 244, 244), radius=int(44 * s), fill=(70, 148, 230, 255))
    # 内圆角矩形 - 淡蓝填充
    d.rounded_rectangle(r(24, 24, 232, 232), radius=int(36 * s), fill=(130, 195, 255, 255))

    # 相机主体（白色）
    d.rounded_rectangle(r(52, 82, 204, 182), radius=int(18 * s), fill=(255, 255, 255, 240))

    # 相机内部（淡蓝）
    d.rounded_rectangle(r(60, 90, 196, 174), radius=int(14 * s), fill=(100, 175, 245, 255))

    # 镜头外圈（白色）
    d.ellipse(r(96, 98, 160, 162), fill=(255, 255, 255, 255))
    # 镜头中圈（淡蓝）
    d.ellipse(r(106, 108, 150, 152), fill=(90, 168, 247, 255))
    # 镜头高光（白色）
    d.ellipse(r(118, 120, 138, 140), fill=(255, 255, 255, 200))

    # 闪光灯（白色小方块）
    d.rounded_rectangle(r(118, 68, 148, 86), radius=int(5 * s), fill=(255, 255, 255, 220))

    return img


if __name__ == "__main__":
    img = generate_icon(256)

    # 保存 PNG
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    img.save(png_path, "PNG")
    print(f"PNG 图标已保存: {png_path}")

    # 保存 ICO（多尺寸）
    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=sizes)
    print(f"ICO 图标已保存: {ico_path}")

    # 保存不同尺寸的 PNG
    for sz in [16, 32, 48, 64, 128]:
        resized = img.resize((sz, sz), Image.LANCZOS)
        path = os.path.join(ASSETS_DIR, f"icon_{sz}.png")
        resized.save(path, "PNG")
        print(f"  {sz}x{sz} 已保存: {path}")

    print("图标生成完成!")
