# N.E.O.N — Autonomous AI Research Agent

N.E.O.N is an advanced, modular AI research agent designed to autonomously execute complex workflows, gather data, and generate insights. Built with Python, it features a rich ecosystem of integrated tools (Skills), persistent memory management, and a dual Desktop/Web user interface.

## System Architecture

The agent operates on a tool-calling architecture, allowing the core LLM to intelligently route tasks to specific execution modules based on user prompts.

- **Core Engine:** Handles prompt engineering, system instructions (`system_prompt.py`), and context window management.
- **Memory Subsystem:** Implements stateful interactions (`memory_skill.py`) to maintain context across prolonged research sessions.
- **UI/UX Layer:** Dual-interface support featuring a web UI built with Streamlit (`.streamlit/`) and a dedicated desktop application wrapper (`desktop_app.py`).

## Integrated Skills & Capabilities

N.E.O.N is equipped with a dynamic skill system that allows it to interact with the external environment and generate tangible outputs:

- **Search & Scrape:** Real-time web searching (`searchskill.py`) and content extraction (`scrapeskill.py`).
- **Document Generation:** Automated creation of PDF reports (`pdf_create.py`, `pdf_skill.py`).
- **Data Manipulation:** Direct reading and writing of Excel spreadsheets (`excel_skill.py`).
- **Voice Interaction:** Speech processing capabilities (`voiceskill.py`).
- **OS Integration:** Local file system management and execution (`fileskill.py`, `os_tools.py`).

## Tech Stack

- **Language:** Python 3
- **Frontend/UI:** Streamlit, HTML/CSS (`styles/`)
- **Architecture:** Modular Agentic Framework, Multi-Tool Integration
- **Execution:** Multi-environment (Local Desktop via VBScript/Python runner & Web Server)

## Getting Started

### Prerequisites
- Python 3 (tested with 3.13)
- [Ollama](https://ollama.com) running locally, with the default model downloaded:
  ```bash
  ollama pull qwen2.5:3b
  ```
- No paid API key is needed for the default setup. Web search uses DuckDuckGo. To use a different local model, set `OLLAMA_MODEL` (see [Configuration](#configuration)).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MoranAshkenazi/N.E.O.N..git
   cd N.E.O.N.
   ```
2. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Start the web interface (Streamlit):
   ```bash
   python -m streamlit run app.py
   ```
   Then open the URL that Streamlit prints (by default http://localhost:8501).

Optional:
- **REST API:** `python server.py` starts FastAPI on port 8000. The `static/` folder is served from the current directory, so run the command from the project folder.
- **Desktop window (Windows):** `pip install -r requirements-desktop.txt`, then `python desktop_runner.py`. `launch_neon.vbs` expects a virtual environment named `venv` in the project folder.

### Configuration
Create a `.env` file in the project folder (it is git-ignored). Supported variables:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5:3b` | Name of the local Ollama model the agent uses |
