import math
from PIL import Image, ImageDraw, ImageFilter

def create_neon_icon():
    size = (256, 256)
    img = Image.new("RGBA", size, (5, 10, 20, 255))
    cx, cy = 128, 128

    # Background radial glow
    glow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    for r in range(120, 10, -5):
        alpha = int((1.0 - r / 120.0) * 80)
        glow_draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 243, 255, alpha))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, glow_layer)

    # Outer tactical radar ring
    vector_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vector_layer)
    v_draw.ellipse((cx - 105, cy - 105, cx + 105, cy + 105), outline=(0, 150, 255, 120), width=2)
    v_draw.ellipse((cx - 115, cy - 115, cx + 115, cy + 115), outline=(0, 243, 255, 60), width=1)

    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        x1 = cx + 105 * math.cos(rad)
        y1 = cy + 105 * math.sin(rad)
        x2 = cx + 115 * math.cos(rad)
        y2 = cy + 115 * math.sin(rad)
        v_draw.line([(x1, y1), (x2, y2)], fill=(0, 243, 255, 200), width=2)

    # Tactical 'N' Core
    n_glow = Image.new("RGBA", size, (0, 0, 0, 0))
    n_glow_draw = ImageDraw.Draw(n_glow)

    p_left_top, p_left_bot = (70, 55), (70, 201)
    p_right_top, p_right_bot = (186, 55), (186, 201)

    for w, alpha in [(18, 40), (14, 70), (10, 120), (6, 200)]:
        n_glow_draw.line([p_left_bot, p_left_top, p_right_bot, p_right_top], fill=(0, 243, 255, alpha), width=w, joint="curve")
        n_glow_draw.polygon([(cx, cy - 18), (cx + 18, cy), (cx, cy + 18), (cx - 18, cy)], outline=(0, 243, 255, alpha), fill=(0, 243, 255, alpha // 2))

    n_glow = n_glow.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, n_glow)

    # Sharp Foreground
    fg_layer = Image.new("RGBA", size, (0, 0, 0, 0))
    fg_draw = ImageDraw.Draw(fg_layer)
    fg_draw.line([p_left_bot, p_left_top, p_right_bot, p_right_top], fill=(210, 250, 255, 255), width=5, joint="curve")
    fg_draw.polygon([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)], outline=(255, 255, 255, 255), fill=(0, 243, 255, 200))

    for nx, ny in [p_left_top, p_left_bot, p_right_top, p_right_bot]:
        fg_draw.ellipse((nx - 6, ny - 6, nx + 6, ny + 6), fill=(0, 243, 255, 255), outline=(255, 255, 255, 255), width=2)

    img = Image.alpha_composite(img, vector_layer)
    img = Image.alpha_composite(img, fg_layer)

    # Save as ICO for Windows
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("neon_icon.ico", format="ICO", sizes=icon_sizes)
    print("-> Successfully created neon_icon.ico")

if __name__ == "__main__":
    create_neon_icon()