import { useEffect, useState } from 'react';
import { LANGUAGES } from '../../config/languages';
import { registerOnlineSync, pendingCount } from './offlineQueue';

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
  const [language, setLanguage] = useState(() => localStorage.getItem('arogyasetu-language') || 'en');
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [online, setOnline] = useState(navigator.onLine);
  const [pending, setPending] = useState(0);

  useEffect(() => {
    localStorage.setItem('arogyasetu-language', language);
  }, [language]);

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    const cleanup = registerOnlineSync(API, 'web-device', async () => setPending(await pendingCount()));
    void pendingCount().then(setPending);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      cleanup();
    };
  }, []);

  async function analyze() {
    if (!text.trim() || !online) return;
    setBusy(true);
    try {
      const response = await fetch(`${API}/pipeline/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language, vitals: {}, history: [] })
      });
      if (!response.ok) throw new Error(`Pipeline failed: ${response.status}`);
      setResult(await response.json());
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : 'Backend unavailable.' });
    } finally { setBusy(false); }
  }

  const triage = result?.triage;
  const symptoms = result?.symptoms?.symptoms || [];
  const referral = result?.referral?.recommended_facility;

  return <main className="app-shell">
    <header>
      <div>
        <span className="eyebrow">AROGYASETU AI</span>
        <h1>Rural Healthcare Orchestrator</h1>
        <p>Multilingual, offline-first decision support for ASHA workflows.</p>
      </div>
      <div className="status-stack">
        <span className="demo">SYNTHETIC DEMO</span>
        <span className={`connectivity ${online ? 'online' : 'offline'}`}>{online ? '● Online' : '○ Offline'} · {pending} pending</span>
      </div>
    </header>

    <section className="card">
      <label>Patient language</label>
      <select value={language} onChange={e => setLanguage(e.target.value)}>
        {LANGUAGES.map((l: any) => <option key={l.code} value={l.code}>{l.nativeName || l.name} · {l.name}</option>)}
      </select>

      <label>Voice transcript / symptoms</label>
      <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Enter or transcribe patient symptoms..." rows={6}/>
      <button onClick={analyze} disabled={busy || !online || !text.trim()}>
        {busy ? 'Analyzing…' : online ? 'Run Clinical Decision Pipeline' : 'Offline — queued actions only'}
      </button>
    </section>

    {result && !result.error && <section className="card result">
      <h2>AI-assisted assessment</h2>
      <div className={`risk-indicator ${riskClass(triage?.risk_level)}`}>
        <div className="risk-title">{triage?.risk_level || 'UNKNOWN'} RISK</div>
        <div className="risk-score">{triage?.risk_score ?? '—'}<span>/100</span></div>
        <div className="risk-label">{triage?.risk_label || 'Requires professional review'}</div>
        <div className="risk-bar"><span style={{ width: `${Math.min(100, Math.max(0, triage?.risk_score ?? 0))}%` }} /></div>
      </div>

      <div className="result-grid">
        <div><strong>Triage</strong><p>{triage?.triage_level || 'Unavailable'}</p></div>
        <div><strong>Confidence</strong><p>{triage?.confidence_percent ?? ((triage?.confidence ?? 0) * 100).toFixed(1)}%</p></div>
        <div><strong>Symptoms</strong><p>{symptoms.length ? symptoms.join(', ') : 'No known symptom match'}</p></div>
        <div><strong>Referral</strong><p>{referral?.name || 'Professional review required'}</p></div>
      </div>

      <p>{triage?.recommended_action}</p>
      {triage?.human_review_required && <p className="notice warning">⚠ Human healthcare professional review required.</p>}
      {referral && <p className="notice">Referral rationale: {result.referral.reason || 'Synthetic demo recommendation.'}</p>}
      <p className="notice">AI-assisted decision support only — not a medical diagnosis.</p>
    </section>}

    {result?.error && <section className="card result"><h2>Service unavailable</h2><p>{result.error}</p></section>}
    <footer>AI-assisted decision support only — not a diagnosis.</footer>
  </main>;
}
