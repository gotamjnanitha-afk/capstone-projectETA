import { useState } from "react";
import { Upload, ScanSearch, Wrench, Play, Download, ShieldCheck, Bug, Code2, CheckCircle2, AlertTriangle } from "lucide-react";

const API = "http://127.0.0.1:8000";
const sample = `def calculate_average(numbers):
    total = 0
    for i in range(len(numbers) + 1):
        total += numbers[i]
    average = total / len(numbers)
    return average

marks = [80, 90, 70]
print("Average:", calculate_average(marks))
`;

export default function App() {
  const [code, setCode] = useState(sample);
  const [tests, setTests] = useState(`from submitted import calculate_average

def test_normal_list():
    assert calculate_average([80, 90, 70]) == 80

def test_two_values():
    assert calculate_average([10, 20]) == 15

def test_empty_list():
    assert calculate_average([]) == 0
`);
  const [review, setReview] = useState(null);
  const [fix, setFix] = useState(null);
  const [run, setRun] = useState(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  async function request(path, body) {
    const res = await fetch(`${API}/api/${path}`, {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
  }
  async function act(name, fn) {
    setBusy(name); setError("");
    try { await fn(); } catch (e) { setError(e.message); }
    finally { setBusy(""); }
  }
  function upload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { setCode(String(reader.result || "")); setReview(null); setFix(null); setRun(null); };
    reader.readAsText(file);
  }
  function download() {
    const blob = new Blob([fix?.fixed_code || code], {type:"text/x-python"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "fixed_code.py"; a.click();
    URL.revokeObjectURL(url);
  }

  return <div className="shell">
    <header className="topbar">
      <div className="brand"><div className="brandIcon"><Code2 size={22}/></div><div><b>CodePilot AI</b><small>Autonomous Code Review & Repair</small></div></div>
      <div className="status"><span className="dot"/> AI Developer Workspace</div>
    </header>
    <main>
      <section className="hero">
        <div><div className="eyebrow">AGENTIC AI · SOFTWARE ENGINEERING</div><h1>Find bugs. Understand them.<br/><span>Fix with confidence.</span></h1><p>Analyze Python code, get AI-powered review, generate a repair and validate it in an isolated Docker environment.</p></div>
        <div className="heroMark"><ShieldCheck size={54}/><span>Review → Repair → Verify</span></div>
      </section>
      {error && <div className="error"><AlertTriangle size={18}/>{error}</div>}
      <section className="workspace">
        <div className="panel editorPanel">
          <div className="panelHead"><div><Code2 size={18}/><b>Source code</b><span className="tag">PYTHON</span></div><label className="upload"><Upload size={15}/> Upload .py<input type="file" accept=".py,.txt" onChange={upload}/></label></div>
          <textarea spellCheck="false" value={code} onChange={e=>{setCode(e.target.value);setReview(null);setFix(null);setRun(null);}}/>
          <div className="editorFoot"><span>{code.split("\n").length} lines · {code.length} characters</span><button className="primary" disabled={!!busy || !code.trim()} onClick={()=>act("review",async()=>setReview(await request("review",{code,filename:"submitted.py"})))}><ScanSearch size={16}/>{busy==="review"?"Reviewing...":"Review code"}</button></div>
        </div>
        <div className="panel resultPanel">
          <div className="panelHead"><div><Bug size={18}/><b>Review results</b></div><span className="tag">ANALYSIS</span></div>
          {!review ? <div className="empty"><ScanSearch size={34}/><b>No review yet</b><span>Click “Review code” to analyze your source.</span></div> :
            <div className="results">
              <div className="metricRow"><div className="metric"><strong>{review.findings.length}</strong><span>Findings</span></div><div className="metric"><strong>{review.syntax_valid?"Valid":"Invalid"}</strong><span>Syntax</span></div><div className="metric"><strong>{review.ruff_available?"On":"Off"}</strong><span>Ruff</span></div></div>
              <p className="summary">{review.summary}</p>
              {review.findings.map((f,i)=><div className="finding" key={i}><div className="findingTop"><span className={`severity ${f.severity}`}>{f.severity}</span><b>{f.category}</b>{f.line && <small>Line {f.line}</small>}</div><p>{f.message}</p>{f.suggestion && <small>Suggestion: {f.suggestion}</small>}</div>)}
              {review.ai_review && <div className="aiText"><b>AI reviewer notes</b><pre>{review.ai_review}</pre></div>}
            </div>}
        </div>
      </section>
      <section className="panel fixPanel">
        <div className="panelHead"><div><Wrench size={18}/><b>AI repair</b></div><button className="secondary" disabled={!!busy || !code.trim()} onClick={()=>act("fix",async()=>{setFix(await request("fix",{code,filename:"submitted.py"}));setRun(null);})}>{busy==="fix"?"Generating...":"Generate fix"}</button></div>
        {fix ? <><div className="fixMeta"><CheckCircle2 size={16}/> Suggested repair generated · Review it before using</div><div className="split"><div><label>Original code</label><pre>{code}</pre></div><div><label>Fixed code</label><pre>{fix.fixed_code}</pre></div></div><p className="summary">{fix.explanation}</p><ul>{(fix.changes||[]).map((x,i)=><li key={i}>{x}</li>)}</ul><button className="primary" onClick={()=>setCode(fix.fixed_code)}>Use fixed code in editor</button> <button className="secondary" onClick={download}><Download size={15}/> Download fixed .py</button></> : <div className="hint">Run a review, then generate an AI-proposed correction. Ollama must be running for this feature.</div>}
      </section>
      <section className="panel testPanel">
        <div className="panelHead"><div><Play size={18}/><b>Sandbox verification</b></div><span className="tag">DOCKER ISOLATION</span></div>
        <label className="fieldLabel">Pytest test cases</label><textarea className="tests" spellCheck="false" value={tests} onChange={e=>setTests(e.target.value)}/>
        <div className="testActions"><span>Runs only when Docker is installed and running.</span><button className="primary" disabled={!!busy || !code.trim()} onClick={()=>act("run",async()=>setRun(await request("run-tests",{code,tests,filename:"submitted.py"})))}><Play size={15}/>{busy==="run"?"Running...":"Run isolated tests"}</button></div>
        {run && <div className={`runResult ${run.passed?"passed":"failed"}`}><b>{run.passed?"Tests passed":"Tests not passed / unavailable"}</b><pre>{run.stdout || run.stderr || run.message || "No output"}{run.message ? "" : run.stderr}</pre></div>}
      </section>
      <footer>CodePilot AI · Educational prototype · Always inspect AI-generated code before accepting it.</footer>
    </main>
  </div>;
}
