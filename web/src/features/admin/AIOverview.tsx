import { useEffect, useState } from 'react';

interface ModelStatus {
  task: string;
  model_id: string | null;
  version: string;
  demo_only: boolean;
  metrics: Record<string, unknown>;
  created_at: string | null;
}

const TASK_LABELS: Record<string, string> = {
  classify: 'Material Classifier',
  valuation: 'Price Estimator',
  anomaly: 'Anomaly Detector',
  forecast: 'Price Forecast',
  matching: 'Recycler Matching',
};

const GATE_INFO: Record<string, string> = {
  classify: '≥60 verified images/class, macro-F1 ≥0.80',
  valuation: '≥200 real transactions/material',
  anomaly: '≥300 real transactions + rule engine always-on',
  forecast: '≥30 real calendar days of price data',
  matching: 'Always-on (6-weight rules, DB weights)',
};

export default function AIOverview() {
  const [tasks, setTasks] = useState<ModelStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/admin/ml/overview')
      .then(r => r.json())
      .then(d => { setTasks(d.tasks); setLoading(false); })
      .catch(() => { setError('Failed to load AI overview'); setLoading(false); });
  }, []);

  if (loading) return <div className="admin-loading">Loading AI status…</div>;
  if (error) return <div className="admin-error">{error}</div>;

  return (
    <div className="ai-overview">
      <div className="page-header">
        <h1 className="page-title">AI &amp; Model Overview</h1>
        <p className="page-subtitle">
          Active models per task · Data gate status · All models are{' '}
          <span className="badge badge-demo">demo_only</span> until field data gates are met
        </p>
      </div>

      <div className="ai-task-grid">
        {tasks.map(t => (
          <div key={t.task} className={`ai-task-card ${t.demo_only ? 'demo' : 'live'}`}>
            <div className="task-header">
              <span className="task-name">{TASK_LABELS[t.task] ?? t.task}</span>
              <span className={`task-badge ${t.demo_only ? 'badge-demo' : 'badge-live'}`}>
                {t.demo_only ? 'Demo only' : 'Live'}
              </span>
            </div>
            <div className="task-version">Version: {t.version}</div>
            <div className="task-gate">
              <strong>Gate:</strong> {GATE_INFO[t.task] ?? '—'}
            </div>
            {t.metrics && Object.keys(t.metrics).length > 0 && (
              <div className="task-metrics">
                {Object.entries(t.metrics).map(([k, v]) => (
                  <span key={k} className="metric-chip">
                    {k}: {typeof v === 'number' ? (v as number).toFixed(3) : String(v)}
                  </span>
                ))}
              </div>
            )}
            {t.demo_only && (
              <p className="demo-note">
                Suggestions are illustrative only. No real verified training data collected yet.
              </p>
            )}
          </div>
        ))}
      </div>

      <style>{`
        .ai-overview { padding: 2rem; }
        .page-header { margin-bottom: 2rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .4rem; }
        .page-subtitle { color: var(--text-secondary); margin: 0; font-size: .95rem; }
        .ai-task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.25rem; }
        .ai-task-card { background: var(--card-bg, #1e2330); border: 1px solid var(--border, #2a3040);
          border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: .6rem; }
        .ai-task-card.demo { border-left: 3px solid #f59e0b; }
        .ai-task-card.live { border-left: 3px solid #10b981; }
        .task-header { display: flex; justify-content: space-between; align-items: center; }
        .task-name { font-weight: 600; font-size: 1rem; }
        .task-badge, .badge { display: inline-block; padding: .2rem .6rem; border-radius: 6px;
          font-size: .75rem; font-weight: 600; }
        .badge-demo { background: rgba(245,158,11,.15); color: #f59e0b; }
        .badge-live { background: rgba(16,185,129,.15); color: #10b981; }
        .task-version, .task-gate { font-size: .82rem; color: var(--text-secondary, #94a3b8); }
        .task-metrics { display: flex; flex-wrap: wrap; gap: .4rem; }
        .metric-chip { background: rgba(99,102,241,.12); color: #818cf8;
          padding: .15rem .5rem; border-radius: 6px; font-size: .75rem; }
        .demo-note { font-size: .78rem; color: #f59e0b; margin: .25rem 0 0;
          padding: .5rem; background: rgba(245,158,11,.07); border-radius: 6px; }
        .admin-loading, .admin-error { padding: 2rem; color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
