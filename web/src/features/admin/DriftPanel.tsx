import { useEffect, useState } from 'react';

interface DriftPoint {
  id: string;
  task: string;
  metric_name: string;
  value: number;
  threshold: number;
  status: string;
  window_start: string;
  window_end: string;
}

const METRIC_LABELS: Record<string, string> = {
  psi_class_dist: 'Class Distribution PSI',
  override_rate: 'User Override Rate',
  not_sure_rate: '"Not Sure" Rate',
  price_psi: 'Price Feature PSI',
};

const STATUS_COLOR: Record<string, string> = {
  ok: '#10b981',
  warn: '#f59e0b',
  alert: '#ef4444',
};

export default function DriftPanel() {
  const [data, setData] = useState<DriftPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [taskFilter, setTaskFilter] = useState('classify');

  useEffect(() => {
    setLoading(true);
    fetch(`/api/admin/ml/drift?task=${taskFilter}&days=30`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [taskFilter]);

  const grouped = data.reduce<Record<string, DriftPoint[]>>((acc, d) => {
    (acc[d.metric_name] ??= []).push(d);
    return acc;
  }, {});

  return (
    <div className="drift-panel">
      <div className="page-header">
        <h1 className="page-title">Drift Monitoring</h1>
        <p className="page-subtitle">
          Nightly snapshots of PSI, override rate, and "not sure" rate over the last 30 days.
          <strong> alert</strong> = retrain recommended.
        </p>
      </div>

      <div className="filter-row">
        {['classify', 'valuation', 'anomaly'].map(t => (
          <button key={t} id={`drift-tab-${t}`}
            className={`tab-btn ${taskFilter === t ? 'active' : ''}`}
            onClick={() => setTaskFilter(t)}>
            {t}
          </button>
        ))}
      </div>

      {loading && <div className="admin-loading">Loading drift data…</div>}

      {!loading && data.length === 0 && (
        <div className="empty-state">
          No drift snapshots yet for <strong>{taskFilter}</strong>.
          <br />Snapshots are written nightly by the drift monitoring job.
        </div>
      )}

      {!loading && Object.entries(grouped).map(([metric, points]) => {
        const latest = points[0];
        return (
          <div key={metric} className="drift-card">
            <div className="drift-card-header">
              <span className="metric-name">{METRIC_LABELS[metric] ?? metric}</span>
              <span className="latest-val" style={{ color: STATUS_COLOR[latest?.status] ?? '#94a3b8' }}>
                {latest ? `${(latest.value * 100).toFixed(2)}%` : '—'}
              </span>
              <span className="drift-status-badge"
                style={{ background: `${STATUS_COLOR[latest?.status] ?? '#94a3b8'}20`,
                         color: STATUS_COLOR[latest?.status] ?? '#94a3b8' }}>
                {latest?.status ?? '—'}
              </span>
            </div>
            <div className="drift-sparkline">
              {points.slice(0, 14).reverse().map((p, i) => (
                <div key={i} className="bar-wrap" title={`${new Date(p.window_end).toLocaleDateString()}: ${(p.value * 100).toFixed(1)}%`}>
                  <div className="bar" style={{
                    height: `${Math.min(100, (p.value / (p.threshold * 2)) * 100)}%`,
                    background: STATUS_COLOR[p.status] ?? '#6366f1',
                  }} />
                </div>
              ))}
            </div>
            <div className="threshold-note">
              Threshold: {(latest?.threshold * 100).toFixed(1)}% ·
              Window: {points.length} day(s)
            </div>
          </div>
        );
      })}

      <style>{`
        .drift-panel { padding: 2rem; }
        .page-header { margin-bottom: 1.5rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .4rem; }
        .page-subtitle { color: var(--text-secondary, #94a3b8); font-size: .9rem; margin: 0; }
        .filter-row { display: flex; gap: .5rem; margin-bottom: 1.5rem; }
        .tab-btn { padding: .4rem 1rem; border-radius: 8px; border: 1px solid var(--border, #2a3040);
          background: transparent; color: var(--text-secondary); cursor: pointer; font-size: .88rem;
          transition: all .15s; }
        .tab-btn.active { background: rgba(99,102,241,.15); color: #818cf8; border-color: #6366f1; }
        .drift-card { background: var(--card-bg, #1e2330); border: 1px solid var(--border, #2a3040);
          border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; }
        .drift-card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: .75rem; }
        .metric-name { font-weight: 600; flex: 1; }
        .latest-val { font-size: 1.1rem; font-weight: 700; }
        .drift-status-badge { padding: .2rem .6rem; border-radius: 6px; font-size: .8rem; font-weight: 600; }
        .drift-sparkline { display: flex; align-items: flex-end; gap: 3px; height: 60px;
          padding: .25rem 0; }
        .bar-wrap { flex: 1; height: 100%; display: flex; align-items: flex-end; }
        .bar { width: 100%; border-radius: 2px 2px 0 0; min-height: 2px;
          transition: height .3s; }
        .threshold-note { font-size: .78rem; color: var(--text-secondary); margin-top: .5rem; }
        .empty-state { text-align: center; padding: 3rem; color: var(--text-secondary);
          background: var(--card-bg, #1e2330); border-radius: 12px; }
        .admin-loading { padding: 2rem; color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
