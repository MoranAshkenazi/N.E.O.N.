import os
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def get_default_desktop() -> Path:
  p = Path.home() / "OneDrive" / "Desktop"
  return p if p.exists() else Path.home() / "Desktop"


def _parse_table(table_lines: list, cell_style) -> Table:
  raw_rows = []
  for line in table_lines:
    if re.match(r"^\|?[\s\-:|]+\|?$", line.strip()):
      continue
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    if any(parts):
      raw_rows.append(parts)

  if not raw_rows:
    return None

  header_style = ParagraphStyle(
      "WhiteTableHeader",
      parent=cell_style,
      textColor=colors.white,
      fontName="Helvetica-Bold",
  )

  formatted_table = []
  formatted_table.append(
      [Paragraph(str(cell), header_style) for cell in raw_rows[0]]
  )

  for row in raw_rows[1:]:
    formatted_table.append([Paragraph(str(cell), cell_style) for cell in row])

  tbl = Table(formatted_table, hAlign="LEFT")
  tbl.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("LEFTPADDING", (0, 0), (-1, -1), 10),
          ("RIGHTPADDING", (0, 0), (-1, -1), 10),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#F8FAFC")],
          ),
      ])
  )
  return tbl


def create_pdf(
    filepath: str = None,
    title: str = "Executive Report",
    subtitle: str = None,
    content: str = "",
    path: str = None,
    **kwargs,
) -> str:
  target = filepath or path or kwargs.get("filepath") or kwargs.get("path")
  if not target:
    target = (get_default_desktop() / "document.pdf").as_posix()

  try:
    p = Path(target).expanduser().resolve()
    if p.suffix.lower() != ".pdf":
      p = p.with_suffix(".pdf")

    p.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(p),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0F172A"),
        alignment=0,
        spaceAfter=4,
    )

    h3_style = ParagraphStyle(
        "DocH3",
        parent=styles["Heading3"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # כותרות
    story.append(Paragraph(title, title_style))
    if subtitle:
      story.append(
          Paragraph(
              subtitle,
              ParagraphStyle(
                  "Sub",
                  parent=body_style,
                  textColor=colors.HexColor("#64748B"),
              ),
          )
      )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#E2E8F0"),
            spaceBefore=4,
            spaceAfter=12,
        )
    )

    # נירמול שורות דחוסות עם ||
    normalized_content = content.replace("||", "\n|")
    lines = normalized_content.split("\n")
    i = 0
    while i < len(lines):
      line = lines[i].strip()
      if not line:
        i += 1
        continue

      # זיהוי טקסט של סיכום שנדבק לסוף שורת טבלה
      if line.startswith("|") and ("Summary:" in line or "**Summary" in line):
        parts = re.split(r"(?=\bSummary:|\*\*Summary)", line, maxsplit=1)
        line = parts[0].strip()
        if len(parts) > 1:
          lines.insert(i + 1, parts[1].strip())

      formatted_line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

      # 1. עיבוד טבלאות
      if line.startswith("|"):
        tbl_lines = []
        while i < len(lines) and lines[i].strip().startswith("|"):
          tbl_lines.append(lines[i].strip())
          i += 1
        table_obj = _parse_table(tbl_lines, table_cell_style)
        if table_obj:
          story.append(table_obj)
          story.append(Spacer(1, 0.1 * inch))
        continue

      # 2. עיבוד כותרות
      if formatted_line.startswith("###") or formatted_line.startswith("##"):
        clean_header = formatted_line.lstrip("#").strip()
        story.append(Paragraph(clean_header, h3_style))
      elif formatted_line.endswith(":") and len(formatted_line) < 40:
        story.append(Paragraph(formatted_line, h3_style))

      # 3. עיבוד רשימות
      elif re.match(r"^\d+\.\s+", formatted_line) or formatted_line.startswith(
          ("* ", "- ")
      ):
        clean_bullet = re.sub(r"^(\d+\.|\*|\-)\s+", "", formatted_line)
        story.append(
            Paragraph(
                f"&bull;&nbsp; {clean_bullet}",
                ParagraphStyle("BulletItem", parent=body_style, leftIndent=12),
            )
        )
      else:
        story.append(Paragraph(formatted_line, body_style))

      i += 1

    doc.build(story)
    return (
        f"[SUCCESS]: Enhanced PDF generated successfully at '{p.as_posix()}'"
    )

  except Exception as e:
    return f"[ERROR]: Failed to build PDF: {str(e)}"