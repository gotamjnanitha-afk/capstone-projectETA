# AI Autonomous Code Review and Bug Fixing Agent

A full-stack educational prototype with:
- React + Vite frontend
- FastAPI backend
- Python AST-based static checks
- Optional Ollama LLM integration
- Ruff linting (optional)
- Docker-based isolated execution (optional, recommended)

## Important safety note
This is an educational prototype, not a production-grade secure code execution service.
Never execute untrusted code directly on your host machine. The `/run-tests` endpoint
requires Docker and uses a read-only container filesystem, no network, memory/CPU/PID
limits, and a timeout. Review the Docker configuration before using it.

## Requirements
- Python 3.10+
- Node.js 18+
- Docker Desktop (only for isolated execution)
- Ollama (optional, for AI-generated review/fixes)

## 1. Backend setup (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

## 2. Optional local AI setup
Install Ollama, then pull a coding model:
```powershell
ollama pull qwen2.5-coder:3b
ollama serve
```
Keep Ollama running. The backend uses `OLLAMA_MODEL` (default `qwen2.5-coder:3b`).
If Ollama is unavailable, static analysis still works; AI review/fix features return a
clear message and deterministic static findings remain available.

## 3. Frontend setup (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite (normally http://localhost:5173).

## 4. Docker
Install and start Docker Desktop. The test runner builds a small Python image on first use.
The backend uses Docker only for running submitted source code. If Docker is unavailable,
the review and fix features still work, but isolated test execution will report that Docker
is required.

## Demo
Paste the intentionally buggy sample from `samples/buggy_average.py`, click **Review code**,
then **Generate fix**, and finally **Run tests**. The sample test file is
`samples/test_average.py`.

## Project architecture
- `POST /api/review`: AST checks + optional Ruff + optional LLM review
- `POST /api/fix`: optional LLM repair with strict JSON response; static findings included
- `POST /api/run-tests`: Docker-isolated pytest run
- `GET /api/health`: service status

AI output can be wrong. Always inspect diffs and test results before accepting a fix.
