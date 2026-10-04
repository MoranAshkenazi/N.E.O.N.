import os
import subprocess


def run_shell_command(command: str) -> str:
  """Executes operating system shell commands safely with a timeout."""
  try:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0:
      return (
          f"[Command exited with code {result.returncode}]:\n{stderr or stdout}"
      )
    return stdout if stdout else "[Success: Command executed with no output]"
  except subprocess.TimeoutExpired:
    return "[Error: Command timed out after 30 seconds]"
  except Exception as e:
    return f"[Error executing command]: {str(e)}"