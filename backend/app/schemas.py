from pydantic import BaseModel, Field

class CodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    filename: str = Field(default="submitted.py", max_length=120)

class TestRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    tests: str = Field(default="", max_length=20000)
    filename: str = Field(default="submitted.py", max_length=120)

class Finding(BaseModel):
    severity: str
    category: str
    message: str
    line: int | None = None
    suggestion: str | None = None

class ReviewResponse(BaseModel):
    findings: list[Finding]
    summary: str
    syntax_valid: bool
    ruff_available: bool
    ai_review: str | None = None

class FixResponse(BaseModel):
    fixed_code: str
    explanation: str
    changes: list[str]
    model_used: str
