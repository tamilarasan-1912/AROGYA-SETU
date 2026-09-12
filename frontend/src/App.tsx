import { useState } from 'react';
import { LANGUAGES } from '../../config/languages';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const riskClass = (level?: string) => {
  switch (level) {
    case 'CRITICAL': return 'risk-critical';
    case 'HIGH': return 'risk-high';
    case 'MODERATE': return 'risk-moderate';
    case 'LOW': return 'risk-low';
    default: return 'risk-unknown';
  }
};

export function App() {
  const [language, setLanguage] = useState('en');
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function analyze() {
    if (!text.trim()) return;
    setBusy(true);
    try {
      const response = await fetch(`${API}/triage/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language, vitals: {} })
      });
      setResult(await response.json());
    } catch (error) {
      setResult({ error: 'Backend unavailable. Start the FastAPI service.' });
    } finally { setBusy(false); }
  }

  return <main className="app-shell">
    <header><div><span className="eyebrow">AROGYASETU AI</span><h1>Rural Healthcare Orchestrator</h1><p>Multilingual, offline-first decision support for ASHA workflows.</p></div><span className="demo">SYNTHETIC DEMO</span></header>
    <section className="card">
      <label>Patient language</label>
      <select value={language} onChange={e => setLanguage(e.target.value)}>{LANGUAGES.map((l:any) => <option key={l.code} value={l.code}>{l.nativeName || l.name}</option>)}</select>
      <label>Symptoms</label>
      <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Enter or transcribe patient symptoms..." rows={6}/>
      <button onClick={analyze} disabled={busy}>{busy ? 'Analyzing…' : 'Run AI Triage'}</button>
    </section>
    {result && !result.error && <section className="card result">
      <h2>Triage result</h2>
      <div className={`risk-indicator ${riskClass(result.risk_level)}`}>
        <div className="risk-title">{result.risk_level || 'UNKNOWN'} RISK</div>
        <div className="risk-score">{result.risk_score ?? '—'}<span>/100</span></div>
        <div className="risk-label">{result.risk_label || 'Requires professional review'}</div>
        <div className="risk-bar"><span style={{ width: `${Math.min(100, Math.max(0, result.risk_score ?? 0))}%` }} /></div>
      </div>
      <div className="level">{result.triage_level || 'Unavailable'}</div>
      <p>Model confidence: {result.confidence_percent ?? ((result.confidence ?? 0) * 100).toFixed(1)}%</p>
      <p>{result.recommended_action}</p>
      {result.human_review_required && <p className="notice warning">⚠ Human healthcare professional review required.</p>}
      <p className="notice">AI-assisted decision support only — not a medical diagnosis.</p>
    </section>}
    {result?.error && <section className="card result"><h2>Service unavailable</h2><p>{result.error}</p></section>}
    <footer>AI-assisted decision support only — not a diagnosis.</footer>
  </main>;
}
