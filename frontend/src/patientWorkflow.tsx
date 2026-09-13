import { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

type Patient = { id: string; name: string; age?: number; sex?: string; language?: string };
type Consultation = { id: string; patient_id: string; clinician_name?: string; room_id: string; status: string };

export function PatientWorkflow({ language, online, patientId, onPatientChange }: { language: string; online: boolean; patientId: string | null; onPatientChange: (id: string | null) => void }) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [records, setRecords] = useState<any[]>([]);
  const [consultation, setConsultation] = useState<Consultation | null>(null);
  const [status, setStatus] = useState('');
  const [busy, setBusy] = useState(false);

  async function loadPatients() { if (!online) return; const r = await fetch(`${API}/patients`); if (r.ok) setPatients(await r.json()); }
  async function loadRecords(id: string) { if (!online) return; const r = await fetch(`${API}/patients/${id}/records`); if (r.ok) setRecords((await r.json()).records || []); }
  useEffect(() => { void loadPatients(); }, [online]);
  useEffect(() => { if (patientId) void loadRecords(patientId); else setRecords([]); }, [patientId, online]);

  async function registerPatient() {
    if (!name.trim() || !online) return;
    setBusy(true); setStatus('Registering patient…');
    try {
      const r = await fetch(`${API}/patients`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name.trim(), age: age ? Number(age) : null, sex: sex || null, language }) });
      if (!r.ok) throw new Error(`Registration failed: ${r.status}`);
      const body = await r.json(); const id = body.patient.id;
      setPatients(p => [body.patient, ...p.filter(x => x.id !== id)]); onPatientChange(id); setName(''); setAge(''); setSex(''); setStatus('Patient registered and selected.');
    } catch (e) { setStatus(e instanceof Error ? e.message : 'Registration failed.'); } finally { setBusy(false); }
  }
  async function startConsultation() {
    if (!patientId || !online) return;
    setBusy(true); setStatus('Creating telemedicine room…');
    try {
      const r = await fetch(`${API}/consultations`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patient_id: patientId, status: 'scheduled' }) });
      if (!r.ok) throw new Error(`Consultation failed: ${r.status}`);
      const body = await r.json(); setConsultation(body.consultation); setStatus(`Room ready: ${body.consultation.room_id}`);
    } catch (e) { setStatus(e instanceof Error ? e.message : 'Consultation failed.'); } finally { setBusy(false); }
  }
  async function updateConsultation(next: string) {
    if (!consultation || !online) return;
    const r = await fetch(`${API}/consultations/${consultation.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: next }) });
    if (r.ok) setConsultation(await r.json());
  }

  return <section className="card workflow-card">
    <div className="section-heading"><div><span className="eyebrow">PATIENT WORKFLOW</span><h2>Register & continue care</h2></div><span className="selected-badge">{patientId ? 'Patient selected' : 'No patient selected'}</span></div>
    <div className="form-grid"><input value={name} onChange={e => setName(e.target.value)} placeholder="Patient full name" /><input value={age} onChange={e => setAge(e.target.value)} inputMode="numeric" placeholder="Age" /><select value={sex} onChange={e => setSex(e.target.value)}><option value="">Sex (optional)</option><option value="female">Female</option><option value="male">Male</option><option value="other">Other</option></select><button onClick={registerPatient} disabled={busy || !online || !name.trim()}>Register patient</button></div>
    <div className="patient-selector"><select value={patientId || ''} onChange={e => onPatientChange(e.target.value || null)} disabled={!online}><option value="">Select existing patient…</option>{patients.map(p => <option key={p.id} value={p.id}>{p.name}{p.age ? ` · ${p.age}` : ''}</option>)}</select></div>
    {patientId && <div className="workflow-actions"><button onClick={startConsultation} disabled={busy || !online}>Start telemedicine consultation</button>{consultation && <><span className="room-chip">Room {consultation.room_id}</span>{consultation.status === 'scheduled' && <button onClick={() => updateConsultation('active')}>Join / activate</button>}{consultation.status === 'active' && <button onClick={() => updateConsultation('completed')}>Complete consultation</button>}</>}</div>}
    {status && <p className="helper">{status}</p>}
    {consultation && <div className="consultation-panel"><strong>Telemedicine prototype</strong><p>Status: <b>{consultation.status}</b></p><p>Room: {consultation.room_id}</p><p className="helper">Signaling room is implemented; production media requires authenticated WebRTC and TURN infrastructure.</p></div>}
    {patientId && <div className="records"><div className="section-heading"><h3>Longitudinal health record</h3><button onClick={() => loadRecords(patientId)} disabled={!online}>Refresh</button></div>{records.length ? records.map(r => <article className="record-item" key={r.id}><strong>{r.record_type || 'Encounter'}</strong><time>{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</time><pre>{JSON.stringify(r.payload?.normalized_data || r.payload, null, 2)}</pre></article>) : <p className="helper">No recorded encounters yet. Run the clinical pipeline with this patient selected.</p>}</div>}
  </section>;
}
