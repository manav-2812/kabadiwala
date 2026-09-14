import { useEffect, useState } from 'react';

interface ModelInfo {
  task: string;
  model_id: string | null;
  version: string;
  demo_only: boolean;
  metrics: {
    top1_accuracy?: number;
    macro_f1?: number;
    per_class_recall?: Record<string, number>;
    model_size?: { int8_quantized_size_mb?: number; budget_compliance?: boolean };
    dataset?: string;
    eval_date?: string;
  };
}

const CLASSES = ['CRT','LCD','PCB','CABLE','BATTERY_LI','BATTERY_PB','MOTOR','MAGNET','PLASTIC_MIXED','OTHER'];

export default function ClassifierPanel() {
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [retaining, setRetaining] = useState(false);
  const [retainMsg, setRetainMsg] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/admin/ml/overview')
      .then(r => r.json())
      .then(d => {
        const m = d.tasks?.find((t: ModelInfo) => t.task === 'classify') ?? null;
        setModel(m);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const triggerRetrain = async () => {
    setRetaining(true);
    setRetainMsg('');
    try {
      const res = await fetch('/api/admin/ml/retrain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: 'classify', notes: 'Triggered from Admin UI' }),
      });
      const d = await res.json();
      setRetainMsg(d.message || 'Retrain candidate created');
    } finally {
      setRetaining(false);
    }
  };

  if (loading) return <div className="admin-loading">Loading classifier info…</div>;

  const metrics = model?.metrics ?? {};
  const perClass = metrics.per_class_recall ?? {};
  const macroF1 = metrics.macro_f1;
  const top1 = metrics.top1_accuracy;
  const gateF1 = (macroF1 ?? 0) >= 0.80;
  const gateRecall = Object.values(perClass).every(v => v >= 0.60);
  const gateSize = metrics.model_size?.budget_compliance !== false;

  return (
    <div className="classifier-panel">
      <div className="page-header">
        <h1 className="page-title">Classifier</h1>
        <div className="model-meta">
          <span className="version-tag">v{model?.version ?? 'none'}</span>
          <span className={`status-badge ${model?.demo_only ? 'demo' : 'live'}`}>
            {model?.demo_only ? 'Demo only' : 'Live'}
          </span>
        </div>
        {model?.demo_only && (
          <div className="demo-banner">
            No real model trained yet. Data gate: ≥60 verified images per class (10 classes = 600 min).
            Suggestions shown in the app are illustrative only.
          </div>
        )}
      </div>

      {/* Gate status */}
      <div className="gates-row">
        <div className={`gate-chip ${gateF1 ? 'pass' : 'fail'}`}>
          macro-F1 ≥0.80: {macroF1 != null ? macroF1.toFixed(3) : '—'}
        </div>
        <div className={`gate-chip ${gateRecall ? 'pass' : 'fail'}`}>
          Min class recall ≥0.60: {Object.keys(perClass).length > 0 ? (gateRecall ? 'Pass' : 'Fail') : '—'}
        </div>
        <div className={`gate-chip ${gateSize ? 'pass' : 'fail'}`}>
          Model ≤4 MB: {metrics.model_size?.int8_quantized_size_mb != null
            ? `${metrics.model_size.int8_quantized_size_mb} MB` : '—'}
        </div>
        <div className="gate-chip info">
          Top-1 Acc: {top1 != null ? `${(top1 * 100).toFixed(1)}%` : '—'}
        </div>
      </div>

      {/* Per-class recall */}
      {Object.keys(perClass).length > 0 ? (
        <div className="class-table-wrap">
          <h2 className="section-title">Per-Class Recall</h2>
          <table className="class-table">
            <thead>
              <tr><th>Class</th><th>Recall</th><th>Status</th></tr>
            </thead>
            <tbody>
              {CLASSES.map(c => {
                const val = perClass[c];
                const pass = val != null && val >= 0.60;
                return (
                  <tr key={c} className={val != null && !pass ? 'fail-row' : ''}>
                    <td className="class-name">{c}</td>
                    <td className="recall-bar-cell">
                      {val != null ? (
                        <div className="recall-bar-wrap">
                          <div className="recall-bar" style={{
                            width: `${(val * 100).toFixed(0)}%`,
                            background: pass ? '#10b981' : '#ef4444',
                          }} />
                          <span className="recall-val">{(val * 100).toFixed(1)}%</span>
                        </div>
                      ) : <span className="no-data">—</span>}
                    </td>
                    <td>{val != null ? (pass ? '✓' : '✗ Below gate') : '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-metrics">
          No per-class metrics yet — model has not been trained on real data.
          <br />Run: <code>make -f ml/Makefile ml-train</code> after collecting images.
        </div>
      )}

      {/* Retrain trigger */}
      <div className="retrain-section">
        <h2 className="section-title">Trigger Retrain</h2>
        <p className="retrain-note">
          Creates a candidate record. Training runs manually via <code>make -f ml/Makefile ml-train</code>.
          No auto-activate — admin must approve after eval metrics pass the gate.
        </p>
        <button id="trigger-retrain" onClick={triggerRetrain} disabled={retaining} className="btn btn-primary">
          {retaining ? 'Creating candidate…' : 'Create Retrain Candidate'}
        </button>
        {retainMsg && <div className="retrain-result">{retainMsg}</div>}
      </div>

      <style>{`
        .classifier-panel { padding: 2rem; max-width: 820px; }
        .page-header { margin-bottom: 1.5rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .5rem; }
        .model-meta { display: flex; gap: .75rem; align-items: center; margin-bottom: .5rem; }
        .version-tag { font-size: .82rem; color: var(--text-secondary); }
        .status-badge { padding: .2rem .6rem; border-radius: 6px; font-size: .78rem; font-weight: 600; }
        .status-badge.demo { background: rgba(245,158,11,.15); color: #f59e0b; }
        .status-badge.live { background: rgba(16,185,129,.15); color: #10b981; }
        .demo-banner { background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.3);
          color: #f59e0b; padding: .75rem 1rem; border-radius: 8px; font-size: .88rem; }
        .gates-row { display: flex; flex-wrap: wrap; gap: .75rem; margin-bottom: 1.75rem; }
        .gate-chip { padding: .4rem .9rem; border-radius: 8px; font-size: .85rem; font-weight: 600; }
        .gate-chip.pass { background: rgba(16,185,129,.12); color: #10b981; }
        .gate-chip.fail { background: rgba(239,68,68,.12); color: #f87171; }
        .gate-chip.info { background: rgba(99,102,241,.12); color: #818cf8; }
        .section-title { font-size: 1.1rem; font-weight: 600; margin: 0 0 .75rem; }
        .class-table-wrap { margin-bottom: 2rem; }
        .class-table { width: 100%; border-collapse: collapse; font-size: .88rem; }
        .class-table th { text-align: left; padding: .5rem 1rem; border-bottom: 1px solid var(--border, #2a3040);
          color: var(--text-secondary); font-size: .8rem; text-transform: uppercase; }
        .class-table td { padding: .5rem 1rem; border-bottom: 1px solid rgba(255,255,255,.04); }
        .fail-row { background: rgba(239,68,68,.05); }
        .class-name { font-weight: 600; }
        .recall-bar-wrap { display: flex; align-items: center; gap: .75rem; }
        .recall-bar { height: 8px; border-radius: 4px; min-width: 2px; transition: width .3s; }
        .recall-val { font-size: .82rem; min-width: 3.5rem; }
        .no-data { color: var(--text-secondary); }
        .no-metrics { background: var(--card-bg, #1e2330); border: 1px solid var(--border);
          border-radius: 10px; padding: 1.5rem; color: var(--text-secondary); font-size: .9rem; margin-bottom: 1.5rem; }
        .no-metrics code { background: rgba(99,102,241,.1); padding: .1rem .4rem; border-radius: 4px; color: #818cf8; }
        .retrain-section { background: var(--card-bg, #1e2330); border: 1px solid var(--border);
          border-radius: 12px; padding: 1.25rem; }
        .retrain-note { font-size: .88rem; color: var(--text-secondary); margin: 0 0 1rem; }
        .retrain-note code { background: rgba(99,102,241,.1); padding: .1rem .4rem; border-radius: 4px; color: #818cf8; }
        .retrain-result { margin-top: .75rem; font-size: .85rem; color: #10b981; background: rgba(16,185,129,.08);
          padding: .6rem .9rem; border-radius: 6px; }
        .btn { padding: .6rem 1.4rem; border-radius: 8px; border: none; cursor: pointer;
          font-weight: 600; font-size: .9rem; }
        .btn-primary { background: #6366f1; color: #fff; }
        .btn:disabled { opacity: .4; cursor: not-allowed; }
        .admin-loading { padding: 2rem; color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
