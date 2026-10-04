import ast
import io
import json
import os
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference


def get_default_desktop() -> Path:
  p = Path.home() / "OneDrive" / "Desktop"
  return p if p.exists() else Path.home() / "Desktop"


def create_excel(
    filepath: str = None,
    data: list | str = None,
    sheet_name: str = "Summary",
    chart_type: str = "bar",
    chart_title: str = "Overview",
    path: str = None,
    **kwargs,
) -> str:
  """Creates an Excel spreadsheet with a chart.

  Args:
      filepath: Full absolute path for the .xlsx file on Desktop.
      data: List of dicts representing rows, e.g. [{"Provider": "AWS",
        "Share": 32}, {"Provider": "Azure", "Share": 23}]
      sheet_name: Name of worksheet.
      chart_type: 'bar', 'line', or 'pie'.
      chart_title: Title of chart.
  """
  target = filepath or path or kwargs.get("filepath") or kwargs.get("path")
  raw_data = data or kwargs.get("data")
  c_type = (chart_type or kwargs.get("chart_type") or "bar").lower().strip()
  c_title = (
      chart_title
      or kwargs.get("chart_title")
      or kwargs.get("title")
      or "Overview"
  )

  if not raw_data or raw_data == "[]":
    return "[ERROR]: No data provided to write to Excel."

  default_filename = (
      "ev_comparison.xlsx"
      if "ev" in str(raw_data).lower()
      else "summary.xlsx"
  )

  if not target:
    p = get_default_desktop() / default_filename
  else:
    clean = str(target).replace("\\", "/").rstrip("/")
    target_path = Path(clean)

    if target_path.is_dir() or target_path.name in ["Desktop", "OneDrive"]:
      p = get_default_desktop() / default_filename
    elif not os.path.isabs(clean) or clean.startswith("~"):
      filename = target_path.name if target_path.name else default_filename
      p = get_default_desktop() / filename
    else:
      if not target_path.suffix:
        p = (
            target_path / default_filename
            if target_path.exists()
            else get_default_desktop() / default_filename
        )
      else:
        p = target_path

  if p.suffix.lower() != ".xlsx":
    p = p.with_suffix(".xlsx")

  try:
    p.parent.mkdir(parents=True, exist_ok=True)

    df = None
    if isinstance(raw_data, str):
      clean_str = raw_data.strip()
      for parser in [ast.literal_eval, json.loads]:
        try:
          parsed = parser(clean_str)
          if isinstance(parsed, (list, dict)):
            df = pd.DataFrame(parsed)
            break
        except Exception:
          pass

      if df is None:
        try:
          df = pd.read_csv(io.StringIO(clean_str))
        except Exception:
          pass
    elif isinstance(raw_data, (list, dict)):
      df = pd.DataFrame(raw_data)

    if df is None or df.empty:
      return "[ERROR]: Data could not be parsed into a valid table."

    # ארגון עמודות קשיח: איתור העמודה הראשונה שאינה מספרית והצבתה בהתחלה כקטגוריות
    cols = list(df.columns)
    cat_col = None
    for col in cols:
      if not pd.api.types.is_numeric_dtype(df[col]):
        cat_col = col
        break

    if cat_col and cat_col != cols[0]:
      reordered = [cat_col] + [c for c in cols if c != cat_col]
      df = df[reordered]

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    headers = list(df.columns)
    ws.append(headers)

    for row in df.itertuples(index=False):
      ws.append(list(row))

    cats_ref = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)

    if c_type == "pie":
      chart = PieChart()
      chart.title = c_title
      chart.width = 14
      chart.height = 10
      # תרשים עוגה מקבל אך ורק את העמודה המספרית (עמודה 2)
      data_ref = Reference(ws, min_col=2, min_row=1, max_row=len(df) + 1)
      chart.add_data(data_ref, titles_from_data=True)
      chart.set_categories(cats_ref)
    elif c_type == "line":
      chart = LineChart()
      chart.title = c_title
      chart.width = 15
      chart.height = 10
      data_ref = Reference(
          ws, min_col=2, min_row=1, max_col=len(headers), max_row=len(df) + 1
      )
      chart.add_data(data_ref, titles_from_data=True)
      chart.set_categories(cats_ref)
    else:
      chart = BarChart()
      chart.type = "col"
      chart.style = 10
      chart.title = c_title
      chart.y_axis.title = "Value"
      chart.x_axis.title = headers[0]
      chart.width = 15
      chart.height = 10
      data_ref = Reference(
          ws, min_col=2, min_row=1, max_col=len(headers), max_row=len(df) + 1
      )
      chart.add_data(data_ref, titles_from_data=True)
      chart.set_categories(cats_ref)

    ws.add_chart(chart, "F2")

    wb.save(str(p))
    return f"File successfully created at: {p.as_posix()}"

  except Exception as e:
    return f"[ERROR]: Failed to generate Excel file with chart: {str(e)}"