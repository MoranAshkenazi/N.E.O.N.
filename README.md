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
- Python 3.9+
- Valid API keys for the LLM and search services (configured via a local `.env` file).

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/MoranAshkenazi/N.E.O.N..git](https://github.com/MoranAshkenazi/N.E.O.N..git)
   cd N.E.O.N.
