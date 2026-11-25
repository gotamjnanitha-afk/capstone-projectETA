import subprocess
import tempfile
from pathlib import Path

def docker_test(code: str, tests: str) -> dict:
    """Build a pytest image once, then run submitted code in a constrained container."""
    dockerfile_dir = Path(__file__).resolve().parent.parent / "sandbox"
    try:
        build = subprocess.run(
            ["docker", "build", "-t", "codepilot-sandbox:latest", str(dockerfile_dir)],
            capture_output=True, text=True, timeout=180
        )
        if build.returncode != 0:
            return {"available": True, "passed": False,
                    "message": "Could not build the sandbox image. Check Docker and internet access for the first build.",
                    "stderr": build.stderr[-3000:]}
    except FileNotFoundError:
        return {"available": False, "passed": False,
                "message": "Docker was not found. Install and start Docker Desktop."}
    except subprocess.TimeoutExpired:
        return {"available": True, "passed": False,
                "message": "Sandbox image build timed out."}

    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        (work / "submitted.py").write_text(code, encoding="utf-8")
        if tests.strip():
            (work / "test_submitted.py").write_text(tests, encoding="utf-8")
        else:
            (work / "test_submitted.py").write_text(
                "from submitted import *\n"
                "def test_module_imports():\n"
                "    assert True\n", encoding="utf-8"
            )
        command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--read-only",
            "--memory", "128m",
            "--cpus", "0.5",
            "--pids-limit", "64",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
            "-v", f"{work}:/work:ro",
            "-w", "/work",
            "codepilot-sandbox:latest",
            "pytest", "-q"
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=35)
            return {
                "available": True,
                "passed": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout[-6000:],
                "stderr": result.stderr[-3000:]
            }
        except subprocess.TimeoutExpired:
            return {"available": True, "passed": False,
                    "message": "Test execution timed out after 35 seconds."}
