import { useEffect, useState } from 'react';

interface LabelItem {
  id: string;
  photo_id: string;
  label_material_id: string;
  sub_class: string | null;
  source: string;
  verified: boolean;
  training_consent: boolean;
  created_at: string;
}

export default function LabelReviewQueue() {
  const [labels, setLabels] = useState<LabelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [counts, setCounts] = useState({ pending: 0, verified: 0 });

  const load = (verifiedFilter: boolean) => {
    setLoading(true);
    fetch(`/api/admin/labels?verified=${verifiedFilter}&limit=100`)
      .then(r => r.json())
      .then(d => { setLabels(d); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    // Load counts
    Promise.all([
      fetch('/api/admin/labels?verified=false&limit=1000').then(r => r.json()),
      fetch('/api/admin/labels?verified=true&limit=1000').then(r => r.json()),
    ]).then(([pending, verified]) => setCounts({ pending: pending.length, verified: verified.length }));
    load(false);
  }, []);

  const verifyLabel = async (id: string, approved: boolean) => {
    await fetch(`/api/admin/labels/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ verified: approved }),
    });
    setLabels(prev => prev.filter(l => l.id !== id));
  };

  return (
    <div className="label-queue">
      <div className="page-header">
        <h1 className="page-title">Label Review Queue</h1>
        <div className="count-row">
          <span className="count-chip pending">{counts.pending} pending</span>
          <span className="count-chip ok">{counts.verified} verified</span>
        </div>
        <p className="page-subtitle">
          Verify collector-submitted image labels before they enter the training export.
          A label needs <strong>verified=true</strong> AND <strong>training_consent=true</strong> to be exported.
        </p>
      </div>

      {loading && <div className="admin-loading">Loading labels…</div>}

      {!loading && labels.length === 0 && (
        <div className="empty-state">
          No pending labels · All caught up!
        </div>
      )}

      <div className="label-grid">
        {labels.map(l => (
          <div key={l.id} className="label-card">
            <div className="label-info">
              <div className="label-id">Photo: {l.photo_id.slice(0, 12)}…</div>
              <div className="label-material">Material ID: {l.label_material_id.slice(0, 12)}…</div>
              {l.sub_class && <div className="label-sub">Sub-class: {l.sub_class}</div>}
              <div className="label-source">Source: <span className="badge">{l.source}</span></div>
              <div className={`consent-badge ${l.training_consent ? 'ok' : 'missing'}`}>
                Consent: {l.training_consent ? 'Yes' : 'Not yet'}
              </div>
              <div className="label-date">{new Date(l.created_at).toLocaleDateString('en-IN')}</div>
            </div>
            <div className="label-actions">
              <button id={`approve-${l.id}`} className="btn btn-approve"
                onClick={() => verifyLabel(l.id, true)}>
                Approve
              </button>
              <button id={`reject-${l.id}`} className="btn btn-reject"
                onClick={() => verifyLabel(l.id, false)}>
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>

      <style>{`
        .label-queue { padding: 2rem; }
        .page-header { margin-bottom: 2rem; }
        .page-title { font-size: 1.6rem; font-weight: 700; margin: 0 0 .5rem; }
        .page-subtitle { color: var(--text-secondary, #94a3b8); font-size: .9rem; margin: .5rem 0 0; }
        .count-row { display: flex; gap: .75rem; margin: .5rem 0; }
        .count-chip { padding: .25rem .75rem; border-radius: 20px; font-size: .82rem; font-weight: 600; }
        .count-chip.pending { background: rgba(245,158,11,.15); color: #f59e0b; }
        .count-chip.ok { background: rgba(16,185,129,.15); color: #10b981; }
        .label-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .label-card { background: var(--card-bg, #1e2330); border: 1px solid var(--border, #2a3040);
          border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: .75rem; }
        .label-info { display: flex; flex-direction: column; gap: .3rem; font-size: .88rem; }
        .label-id, .label-material { font-family: monospace; color: var(--text-secondary, #94a3b8); }
        .label-source .badge { background: rgba(99,102,241,.12); color: #818cf8;
          padding: .1rem .4rem; border-radius: 4px; font-size: .78rem; }
        .consent-badge { font-size: .8rem; font-weight: 600; }
        .consent-badge.ok { color: #10b981; }
        .consent-badge.missing { color: #f59e0b; }
        .label-date { font-size: .78rem; color: var(--text-secondary); }
        .label-actions { display: flex; gap: .75rem; }
        .btn { padding: .5rem 1.1rem; border-radius: 8px; border: none; cursor: pointer;
          font-weight: 600; font-size: .88rem; transition: opacity .15s; }
        .btn:hover { opacity: .85; }
        .btn-approve { background: #10b981; color: #fff; }
        .btn-reject { background: rgba(239,68,68,.15); color: #f87171; }
        .empty-state { text-align: center; padding: 3rem; color: var(--text-secondary); }
        .admin-loading { padding: 2rem; color: var(--text-secondary); }
      `}</style>
    </div>
  );
}
