from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import CodeRequest, TestRequest
from .analyzer import analyze_python, run_ruff
from .llm import ai_review, ai_fix, OLLAMA_MODEL
from .sandbox import docker_test

app = FastAPI(title="AI Autonomous Code Review Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Code Review Agent", "model": OLLAMA_MODEL}

@app.post("/api/review")
async def review(request: CodeRequest):
    findings, syntax_valid = analyze_python(request.code)
    ruff_findings, ruff_available = run_ruff(request.code)
    findings.extend(ruff_findings)
    ai_text = None
    try:
        ai_text = await ai_review(request.code)
    except Exception as exc:
        ai_text = f"AI model unavailable: {type(exc).__name__}. Static analysis is still available."
    summary = f"Analysis completed. {len(findings)} potential finding(s)."
    return {
        "findings": findings, "summary": summary,
        "syntax_valid": syntax_valid, "ruff_available": ruff_available,
        "ai_review": ai_text
    }

@app.post("/api/fix")
async def fix(request: CodeRequest):
    findings, syntax_valid = analyze_python(request.code)
    if not syntax_valid:
        raise HTTPException(status_code=400, detail="Fix syntax errors before requesting an AI repair.")
    try:
        result = await ai_fix(request.code, findings)
        return {**result, "model_used": OLLAMA_MODEL}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI repair is unavailable ({type(exc).__name__}). Start Ollama and ensure the model is downloaded."
        )

@app.post("/api/run-tests")
async def run_tests(request: TestRequest):
    return docker_test(request.code, request.tests)
