import math
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 500
BG_COLOR = (3, 8, 16, 255)
GRID_COLOR = (0, 238, 255, 18)
CYAN_CORE = (200, 250, 255, 255)
CYAN_GLOW = (0, 243, 255, 255)

# מרכז ה-N הראשונה והכוונת
CX, CY = 218, 248
R_OUTER = 168


def draw_glow_line(draw, glow_draw, p1, p2, width=6, glow_width=18):
  glow_draw.line([p1, p2], fill=(0, 243, 255, 140), width=glow_width)
  draw.line([p1, p2], fill=CYAN_CORE, width=width)


def draw_glow_circle(draw, glow_draw, center, r, width=3, glow_width=12):
  bbox = [center[0] - r, center[1] - r, center[0] + r, center[1] + r]
  glow_draw.ellipse(bbox, outline=(0, 243, 255, 120), width=glow_width)
  draw.ellipse(bbox, outline=CYAN_GLOW, width=width)


# ==========================================
# 1. יצירת neon_logo_base.png (רקע + N + .E.O.N.)
# ==========================================
base_img = Image.new("RGBA", (W, H), BG_COLOR)
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sharp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

draw_base = ImageDraw.Draw(base_img)
draw_glow = ImageDraw.Draw(glow_layer)
draw_sharp = ImageDraw.Draw(sharp_layer)

# רשת רקע טקטית
for x in range(0, W, 30):
  draw_base.line([(x, 0), (x, H)], fill=GRID_COLOR, width=1)
for y in range(0, H, 30):
  draw_base.line([(0, y), (W, y)], fill=GRID_COLOR, width=1)

# N ראשונה (עם העיגולים והיהלום)
n_tl, n_tr = (150, 160), (286, 160)
n_bl, n_br = (150, 336), (286, 336)

draw_glow_line(draw_sharp, draw_glow, n_tl, n_bl, width=7, glow_width=20)
draw_glow_line(draw_sharp, draw_glow, n_tl, n_br, width=7, glow_width=20)
draw_glow_line(draw_sharp, draw_glow, n_tr, n_br, width=7, glow_width=20)

for pt in [n_tl, n_tr, n_bl, n_br]:
  draw_glow.ellipse(
      [pt[0] - 12, pt[1] - 12, pt[0] + 12, pt[1] + 12],
      fill=(0, 243, 255, 180),
  )
  draw_sharp.ellipse(
      [pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7], fill=(255, 255, 255, 255)
  )

diamond = [(CX, CY - 14), (CX + 14, CY), (CX, CY + 14), (CX - 14, CY)]
draw_glow.polygon(diamond, fill=(0, 243, 255, 180))
draw_sharp.polygon(diamond, fill=CYAN_CORE)

# נקודה אחרי ה-N הראשונה
draw_sharp.ellipse([345, 328, 357, 340], fill=CYAN_CORE)

# E
draw_glow_line(
    draw_sharp, draw_glow, (480, 160), (395, 160), width=7, glow_width=20
)
draw_glow_line(
    draw_sharp, draw_glow, (395, 160), (395, 336), width=7, glow_width=20
)
draw_glow_line(
    draw_sharp, draw_glow, (395, 336), (480, 336), width=7, glow_width=20
)
draw_glow_line(
    draw_sharp, draw_glow, (395, 248), (460, 248), width=7, glow_width=20
)
draw_sharp.ellipse([510, 328, 522, 340], fill=CYAN_CORE)

# O (משושה טקטי)
o_pts = [
    (590, 160),
    (670, 160),
    (710, 200),
    (710, 296),
    (670, 336),
    (590, 336),
    (550, 296),
    (550, 200),
    (590, 160),
]
for i in range(len(o_pts) - 1):
  draw_glow_line(
      draw_sharp,
      draw_glow,
      o_pts[i],
      o_pts[i + 1],
      width=7,
      glow_width=20,
  )
draw_sharp.ellipse([740, 328, 752, 340], fill=CYAN_CORE)

# N סופית
draw_glow_line(
    draw_sharp, draw_glow, (780, 336), (780, 160), width=7, glow_width=20
)
draw_glow_line(
    draw_sharp, draw_glow, (780, 160), (915, 336), width=7, glow_width=20
)
draw_glow_line(
    draw_sharp, draw_glow, (915, 336), (915, 160), width=7, glow_width=20
)
draw_sharp.ellipse([935, 328, 947, 340], fill=CYAN_CORE)

# קו תחתון, חץ וכיתוב טקטי
draw_glow_line(
    draw_sharp, draw_glow, (395, 375), (925, 375), width=2, glow_width=10
)
arrow = [(925, 370), (938, 375), (925, 380)]
draw_sharp.polygon(arrow, fill=CYAN_CORE)

draw_sharp.text(
    (395, 395),
    "// TACTICAL RESEARCH & AUTONOMOUS OS AGENT //",
    fill=(93, 147, 187, 255),
)
draw_sharp.text(
    (395, 418),
    "SECURITY PROTOCOL: LEVEL-5 | STATUS: ACTIVE",
    fill=(0, 243, 255, 200),
)

# מיזוג זוהר
glow_blurred = glow_layer.filter(ImageFilter.GaussianBlur(8))
base_final = Image.alpha_composite(base_img, glow_blurred)
base_final = Image.alpha_composite(base_final, sharp_layer)
base_final.save("neon_logo_base.png")
print("Saved: neon_logo_base.png")

# ==========================================
# 2. יצירת neon_ring.png (ריבוע שקוף ממורכז)
# ==========================================
RING_SIZE = 400
ring_img = Image.new("RGBA", (RING_SIZE, RING_SIZE), (0, 0, 0, 0))
r_glow = Image.new("RGBA", (RING_SIZE, RING_SIZE), (0, 0, 0, 0))
r_sharp = Image.new("RGBA", (RING_SIZE, RING_SIZE), (0, 0, 0, 0))

rcx, rcy = RING_SIZE // 2, RING_SIZE // 2
rd_glow = ImageDraw.Draw(r_glow)
rd_sharp = ImageDraw.Draw(r_sharp)

draw_glow_circle(rd_sharp, rd_glow, (rcx, rcy), R_OUTER, width=3, glow_width=14)

ticks = [
    ((rcx, rcy - R_OUTER - 18), (rcx, rcy - R_OUTER + 8)),
    ((rcx, rcy + R_OUTER - 8), (rcx, rcy + R_OUTER + 18)),
    ((rcx - R_OUTER - 18, rcy), (rcx - R_OUTER + 8, rcy)),
    ((rcx + R_OUTER - 8, rcy), (rcx + R_OUTER + 18, rcy)),
]

for angle in [45, 135, 225, 315]:
  rad = math.radians(angle)
  p1 = (
      rcx + int((R_OUTER - 10) * math.cos(rad)),
      rcy + int((R_OUTER - 10) * math.sin(rad)),
  )
  p2 = (
      rcx + int((R_OUTER + 10) * math.cos(rad)),
      rcy + int((R_OUTER + 10) * math.sin(rad)),
  )
  ticks.append((p1, p2))

for p1, p2 in ticks:
  draw_glow_line(rd_sharp, rd_glow, p1, p2, width=3, glow_width=10)

ring_glow_blurred = r_glow.filter(ImageFilter.GaussianBlur(6))
ring_final = Image.alpha_composite(ring_img, ring_glow_blurred)
ring_final = Image.alpha_composite(ring_final, r_sharp)
ring_final.save("neon_ring.png")
print("Saved: neon_ring.png")