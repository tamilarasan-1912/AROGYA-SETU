import { useState } from 'react';
import { LANGUAGES } from '../../config/languages';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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
        method: 'POST', headers: { 'Content-Type': 'application/json' },
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
    {result && <section className="card result"><h2>Triage result</h2><div className="level">{result.triage_level || 'Unavailable'}</div><p>Confidence: {result.confidence ?? '—'}</p><p>{result.recommended_action}</p><p className="notice">{result.disclaimer || 'Human healthcare professional review is required.'}</p></section>}
    <footer>AI-assisted decision support only — not a diagnosis.</footer>
  </main>;
}
