import datetime
import json
import os
from pathlib import Path
import re
import warnings
from dotenv import load_dotenv
import ollama
from prompts.system_prompt import get_system_prompt
from skills.excel_skill import create_excel
from skills.fileskill import delete_file, read_file, write_file
from skills.os_tools import run_shell_command
from skills.pdf_skill import read_pdf
from skills.scrapeskill import read_deep
from skills.searchskill import search_web
from skills.pdf_create import create_pdf
from skills.memory_skill import recall_memory, save_memory
warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

# כלים הדורשים אישור אנושי מפורש
SENSITIVE_TOOLS = {
    "tool_write_file",
    "write_file",
    "tool_delete_file",
    "delete_file",
    "tool_run_shell",
    "run_shell_command",
    "create_excel",
    "create_pdf",
}


def tool_search_web(query: str) -> str:
  """Searches the web for recent news, technical articles, and updates."""
  return search_web(query)


def tool_read_deep(url: str) -> str:
  """Scrapes and reads the full text content of a specific web URL."""
  return read_deep(url)


def tool_write_file(filepath: str, content: str) -> str:
  """Writes or overwrites content into a file on disk."""
  return write_file(filepath=filepath, content=content)


def tool_delete_file(filepath: str = None, **kwargs) -> str:
  """Wrapper עבור כלי המחיקה של הסוכן"""
  target = filepath or kwargs.get("path") or kwargs.get("file_path")
  if not target:
    return "[Error: No filepath provided.]"
  return delete_file(target)


def tool_run_shell(command: str) -> str:
  """Executes an operating system terminal command."""
  return run_shell_command(command)


ALL_SKILLS = [
    tool_search_web,
    tool_read_deep,
    read_pdf,
    create_excel,
    create_pdf,
    tool_write_file,
    tool_delete_file,
    tool_run_shell,
    save_memory,
    recall_memory,
]

SKILL_MAP = {
    "tool_search_web": search_web,
    "search_web": search_web,
    "tool_read_deep": read_deep,
    "read_deep": read_deep,
    "read_pdf": read_pdf,
    "create_excel": create_excel,
    "create_pdf": create_pdf,
    "tool_write_file": write_file,
    "write_file": write_file,
    "tool_delete_file": delete_file,
    "delete_file": delete_file,
    "tool_run_shell": run_shell_command,
    "run_shell_command": run_shell_command,
    "save_memory": save_memory,
    "recall_memory": recall_memory,
}


def execute_skill(name: str, args: dict, authorized: bool = False) -> str:
  if name in SENSITIVE_TOOLS and not authorized:
    return f"[SECURITY_BLOCK]: Action '{name}' is strictly gated and requires human approval."

  # נירמול ארגומנטים למניעת שגיאות פרמטרים
  clean_args = dict(args)
  if "path" in clean_args and "filepath" not in clean_args:
    clean_args["filepath"] = clean_args.pop("path")

  if name in SKILL_MAP:
    try:
      return str(SKILL_MAP[name](**clean_args))
    except Exception as err:
      return f"[Error executing skill {name}]: {str(err)}"
  return f"[Skill {name} not found]"


def execute_single_tool(name: str, args: dict) -> str:
  return execute_skill(name, args, authorized=True)


def _extract_tool_call(text: str):
  if not text:
    return None
  try:
    # 1. תפיסת בלוק ייעודי של תגיות tool_call (נפוץ ב-Qwen)
    tool_block = re.search(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
    raw_json = tool_block.group(1).strip() if tool_block else text

    # 2. חילוץ מילון JSON המכיל name ו-arguments
    match = re.search(
        r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"arguments"\s*:\s*(\{.*?\})\s*\}',
        raw_json,
        re.DOTALL,
    )
    if match:
      return match.group(1), json.loads(match.group(2))

    match_inline = re.search(r'\{"name":\s*"([^"]+)",.*\}', raw_json)
    if match_inline:
      data = json.loads(match_inline.group(0))
      return data.get("name"), data.get("arguments", {})
  except Exception:
    pass
  return None


def run_agent_task(
    user_prompt: str, chat_history: list = None, max_iterations: int = 5
) -> dict:
  prompt = get_system_prompt()
  instr = user_prompt.strip()
  instr_lower = instr.lower()

  if any(
      w in instr_lower
      for w in ["excel", "xlsx", "sheet", "גרף", "אקסל", "טבלה"]
  ):
    active_tools = [create_excel, save_memory, recall_memory]
  elif any(
      w in instr_lower
      for w in ["pdf", "פי די אף", "מסמך", "invitation", "הזמנה"]
  ):
    active_tools = [create_pdf, read_pdf, save_memory, recall_memory]
  elif any(
      w in instr_lower
      for w in ["remember", "תזכור", "שמור", "recall", "העדפה", "preference"]
  ):
    active_tools = [save_memory, recall_memory]
  else:
    active_tools = ALL_SKILLS

  ollama_messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": instr},
  ]

  for _ in range(max_iterations):
    try:
      response = ollama.chat(
          model=OLLAMA_MODEL,
          messages=ollama_messages,
          tools=active_tools,
          keep_alive="24h",
          options={
              "num_ctx": 4096,
              "temperature": 0.1,
              "num_predict": 2048,
          },
      )
    except Exception as e:
      return {"status": "completed", "text": f"[Ollama Execution Error]: {e}"}

    msg = response.get("message", {})
    content = msg.get("content", "")
    tool_calls = msg.get("tool_calls", [])
  

    extracted = _extract_tool_call(content) if not tool_calls else None

    if not tool_calls and not extracted:
      return {
          "status": "completed",
          "text": content if content else "[Task Completed]",
      }

    func_name, func_args = None, {}
    if tool_calls:
      func_name = tool_calls[0]["function"]["name"]
      func_args = tool_calls[0]["function"]["arguments"]
    elif extracted:
      func_name, func_args = extracted

    if func_name in SENSITIVE_TOOLS:
      return {
          "status": "requires_permission",
          "tool_name": func_name,
          "tool_args": func_args,
      }

    out = execute_skill(func_name, func_args, authorized=False)
    ollama_messages.append(msg)
    ollama_messages.append({"role": "tool", "content": str(out)})

  return {"status": "completed", "text": "[Iteration limit reached]"}