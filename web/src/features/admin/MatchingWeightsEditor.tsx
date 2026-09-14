import { useEffect, useState } from 'react';

const DEFAULT_WEIGHTS = {
  payout: 0.30, proximity: 0.25, rate: 0.20,
  pickup: 0.10, reliability: 0.10, response: 0.05,
};

const WEIGHT_LABELS: Record<string, string> = {
  payout: 'Estimated Payout',
  proximity: 'Proximity',
  rate: 'Market Rate',
  pickup: 'Pickup Available',
  reliability: 'Reliability Score',
  response: 'Response Speed',
};

const WEIGHT_DESC: Record<string, string> = {
  payout: 'Recycler\'s bid relative to other recyclers for this lot',
  proximity: 'Shorter distance = higher score (inverted)',
  rate: 'Recycler\'s buy rate vs market band',
  pickup: 'Pickup available bonus (vs drop-off)',
  reliability: 'Historical transaction reliability',
  response: 'Average response time to quotes',
};

export default function MatchingWeightsEditor() {
  const [weights, setWeights] = useState({ ...DEFAULT_WEIGHTS });
  const [version, setVersion] = useState('default');
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  const total = Object.values(weights).reduce((s, v) => s + v, 0);
  const valid = Math.abs(total - 1.0) <= 0.005;

  useEffect(() => {
    fetch('/api/admin/matching-weights')
      .then(r => r.json())
      .then(d => {
        if (d.weights) setWeights(d.weights);
        if (d.version) setVersion(d.version);
      });
  }, []);

  const save = async () => {
    if (!valid) return;
    setSaving(true);
    setMsg('');
    try {
      const res = await fetch('/api/admin/matching-weights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(weights),
      });
      const d = await res.json();
      if (res.ok) {
        setVersion(d.version);
        setMsg(`Saved as ${d.version}`);
      } else {
        setMsg(d.detail || 'Save failed');
      }
    } finally {
      setSaving(false);
    }
  };

  const reset = () => { setWeights({ ...DEFAULT_WEIGHTS }); setMsg(''); };

  return (
    <div className="weights-editor">
      <div className="page-header">
        <h1 className="page-title">Matching Weights Editor</h1>
        <p className="page-subtitle">
          Adjust the 6 scoring factors for the recycler ranking algorithm.
          Weights must sum to <strong>1.00</strong>.
          Changes take effect immediately for new API calls.
        </p>
        <div className="version-row">Active version: <code>{version}</code></div>
      </div>

      <div className="weights-form">
        {Object.entries(weights).map(([key, val]) => (
          <div key={key} className="weight-row">
            <div className="weight-meta">
              <span className="weight-label">{WEIGHT_LABELS[key]}</span>
              <span className="weight-desc">{WEIGHT_DESC[key]}</span>
            </div>
            <div className="weight-control">
              <input
                id={`weight-${key}`}
                type="range"
                min={0} max={0.6} step={0.01}
                value={val}
                onChange={e => setWeights(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                className="slider"
              />
              <span className="weight-val">{(val * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}

        <div className={`total-row ${valid ? 'ok' : 'bad'}`}>
          Total: <strong>{(total * 100).toFixed(1)}%</strong>
          {!valid && <span className="warn"> — must be exactly 100%</span>}
        </div>

        <div className="action-row">
          <button id="save-weights" onClick={save} disabled={!valid || saving}
            className="btn btn-primary">
            {saving ? 'Saving…' : 'Save Weights'}
          </button>
          <button id="reset-weights" onClick={reset} className="btn btn-ghost">
            Reset to Default
          </button>
          {msg && <span className="save-msg">{msg}</span>}
        </div>
      </div>

      <style>{`
        .weights-editor { padding: 2rem; max-width: 680px; }
        .page-header { margin-bottom: 2rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .4rem; }
        .page-subtitle { color: var(--text-secondary, #94a3b8); font-size: .9rem; margin: 0 0 .5rem; }
        .version-row { font-size: .85rem; color: var(--text-secondary); }
        .version-row code { background: rgba(99,102,241,.1); padding: .1rem .4rem; border-radius: 4px; color: #818cf8; }
        .weights-form { display: flex; flex-direction: column; gap: 1.1rem; }
        .weight-row { display: flex; flex-direction: column; gap: .3rem; background: var(--card-bg, #1e2330);
          border: 1px solid var(--border, #2a3040); border-radius: 10px; padding: 1rem; }
        .weight-meta { display: flex; flex-direction: column; gap: .15rem; }
        .weight-label { font-weight: 600; font-size: .95rem; }
        .weight-desc { font-size: .8rem; color: var(--text-secondary, #94a3b8); }
        .weight-control { display: flex; align-items: center; gap: 1rem; margin-top: .4rem; }
        .slider { flex: 1; accent-color: #6366f1; }
        .weight-val { font-weight: 700; font-size: 1rem; width: 3rem; text-align: right; color: #818cf8; }
        .total-row { padding: .75rem 1rem; border-radius: 8px; font-size: .95rem; }
        .total-row.ok { background: rgba(16,185,129,.1); color: #10b981; }
        .total-row.bad { background: rgba(239,68,68,.1); color: #f87171; }
        .warn { font-size: .85rem; margin-left: .5rem; }
        .action-row { display: flex; align-items: center; gap: 1rem; }
        .btn { padding: .6rem 1.4rem; border-radius: 8px; border: none; cursor: pointer;
          font-weight: 600; font-size: .9rem; transition: opacity .15s; }
        .btn:hover:not(:disabled) { opacity: .85; }
        .btn:disabled { opacity: .4; cursor: not-allowed; }
        .btn-primary { background: #6366f1; color: #fff; }
        .btn-ghost { background: var(--card-bg); border: 1px solid var(--border); color: var(--text-secondary); }
        .save-msg { color: #10b981; font-size: .88rem; }
      `}</style>
    </div>
  );
}
