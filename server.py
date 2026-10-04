import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from agent import execute_single_tool, run_agent_task
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from skills.voiceskill import generate_audio_b64
import uvicorn

app = FastAPI(
    title="N.E.O.N. Tactical API",
    description="Core backend service for N.E.O.N. Autonomous Agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
  role: str
  content: str


class AgentTaskRequest(BaseModel):
  prompt: str
  history: Optional[List[ChatMessage]] = []
  max_iterations: Optional[int] = 4


class ExecuteActionRequest(BaseModel):
  tool_name: str
  tool_args: Dict[str, Any]


@app.get("/health")
def health_check():
  return {"status": "ONLINE", "core": "N.E.O.N. Engine Active"}


@app.post("/api/task")
def run_task(req: AgentTaskRequest):
  try:
    raw_history = [{"role": m.role, "content": m.content} for m in req.history]
    result = run_agent_task(
        user_prompt=req.prompt,
        chat_history=raw_history,
        max_iterations=req.max_iterations,
    )

    text_out = result.get("text", "")

    # הורדת קבצים
    if "File successfully created at:" in text_out:
      file_path = text_out.split("File successfully created at:")[-1].strip()
      if os.path.exists(file_path):
        result["download_url"] = f"/api/download?path={file_path}"
        result["filename"] = Path(file_path).name

    # הפקת שמע ישירות מהקול של ניאון
    if text_out:
      try:
        result["audio_b64"] = generate_audio_b64(text_out)
      except Exception:
        result["audio_b64"] = None

    return result
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-action")
def execute_action(req: ExecuteActionRequest):
  try:
    output = execute_single_tool(req.tool_name, req.tool_args)
    return {"tool_name": req.tool_name, "result": output}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download")
def download_file(path: str):
  if not os.path.exists(path):
    raise HTTPException(status_code=404, detail="File not found")
  return FileResponse(
      path, filename=Path(path).name, media_type="application/octet-stream"
  )


app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
  uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)