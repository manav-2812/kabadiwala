import { useEffect, useState } from 'react';

interface Prediction {
  id: string;
  task: string;
  path: string;
  entity_type: string;
  entity_id: string;
  confidence: number;
  latency_ms: number;
  user_override: boolean;
  created_at: string;
}

const TASKS = ['', 'classify', 'valuation', 'anomaly', 'forecast', 'matching'];

export default function PredictionsLog() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [taskFilter, setTaskFilter] = useState('');
  const [overrideOnly, setOverrideOnly] = useState(false);

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams({ limit: '100' });
    if (taskFilter) params.set('task', taskFilter);
    if (overrideOnly) params.set('override_only', 'true');
    fetch(`/api/admin/ml/predictions?${params}`)
      .then(r => r.json())
      .then(d => { setPredictions(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(load, [taskFilter, overrideOnly]);

  const overrideCount = predictions.filter(p => p.user_override).length;

  return (
    <div className="predictions-log">
      <div className="page-header">
        <h1 className="page-title">Predictions Log</h1>
        <p className="page-subtitle">
          Every ML inference call recorded here. Override rate drives retrain suggestions.
        </p>
      </div>

      <div className="filter-bar">
        <select id="task-filter" value={taskFilter}
          onChange={e => setTaskFilter(e.target.value)} className="filter-select">
          <option value="">All tasks</option>
          {TASKS.filter(Boolean).map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <label className="override-toggle">
          <input type="checkbox" checked={overrideOnly}
            onChange={e => setOverrideOnly(e.target.checked)} />
          Overrides only
        </label>
        <span className="override-count">
          {overrideCount} override{overrideCount !== 1 ? 's' : ''} in view
        </span>
      </div>

      {loading && <div className="admin-loading">Loading…</div>}

      {!loading && (
        <div className="table-wrap">
          <table className="pred-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Path</th>
                <th>Entity</th>
                <th>Conf</th>
                <th>Latency</th>
                <th>Override</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map(p => (
                <tr key={p.id} className={p.user_override ? 'override-row' : ''}>
                  <td><span className={`task-pill task-${p.task}`}>{p.task}</span></td>
                  <td className="mono">{p.path}</td>
                  <td className="mono">{p.entity_type}/{p.entity_id.slice(0, 8)}…</td>
                  <td className="conf">{(p.confidence * 100).toFixed(0)}%</td>
                  <td className="latency">{p.latency_ms}ms</td>
                  <td>{p.user_override ? <span className="badge-override">Yes</span> : '—'}</td>
                  <td className="date">{new Date(p.created_at).toLocaleString('en-IN')}</td>
                </tr>
              ))}
              {predictions.length === 0 && (
                <tr><td colSpan={7} className="empty-cell">No predictions logged yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <style>{`
        .predictions-log { padding: 2rem; }
        .page-header { margin-bottom: 1.5rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .4rem; }
        .page-subtitle { color: var(--text-secondary, #94a3b8); margin: 0; font-size: .9rem; }
        .filter-bar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem; }
        .filter-select { background: var(--card-bg, #1e2330); border: 1px solid var(--border, #2a3040);
          color: inherit; padding: .4rem .8rem; border-radius: 8px; font-size: .88rem; }
        .override-toggle { display: flex; align-items: center; gap: .4rem; font-size: .88rem; cursor: pointer; }
        .override-count { font-size: .82rem; color: var(--text-secondary); }
        .table-wrap { overflow-x: auto; }
        .pred-table { width: 100%; border-collapse: collapse; font-size: .87rem; }
        .pred-table th { text-align: left; padding: .6rem 1rem; border-bottom: 1px solid var(--border, #2a3040);
          color: var(--text-secondary); font-weight: 600; font-size: .8rem; text-transform: uppercase; }
        .pred-table td { padding: .6rem 1rem; border-bottom: 1px solid rgba(255,255,255,.04); }
        .override-row { background: rgba(245,158,11,.05); }
        .task-pill { padding: .15rem .5rem; border-radius: 6px; font-size: .78rem; font-weight: 600;
          background: rgba(99,102,241,.12); color: #818cf8; }
        .mono { font-family: monospace; font-size: .82rem; color: var(--text-secondary); }
        .conf { font-weight: 600; }
        .latency { color: var(--text-secondary); }
        .badge-override { background: rgba(245,158,11,.15); color: #f59e0b;
          padding: .1rem .4rem; border-radius: 4px; font-size: .78rem; font-weight: 600; }
        .date { font-size: .78rem; color: var(--text-secondary); }
        .empty-cell { text-align: center; padding: 2rem; color: var(--text-secondary); }
        .admin-loading { padding: 2rem; color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
