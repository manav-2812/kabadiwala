import React, { useEffect, useState } from 'react';
import { apiRequest } from '../../lib/api';
import { LotCard } from '../../design/components/LotCard';
import { Layers, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export const LotsListView: React.FC = () => {
  const [lots, setLots] = useState<any[]>([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    apiRequest('/api/lots?collector_only=true')
      .then((data) => {
        setLots(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = lots.filter((l) => {
    if (filter === 'all') return true;
    if (filter === 'active') return l.status !== 'completed' && l.status !== 'cancelled' && l.status !== 'draft';
    if (filter === 'completed') return l.status === 'completed';
    return true;
  });

  return (
    <div className="flex flex-col gap-4 pb-6">
      <div className="flex items-center justify-between border-b border-[#E3E0D5] pb-2">
        <div className="flex items-center gap-2">
          <Layers size={22} className="text-[#0B3D2E]" />
          <h2 className="text-lg font-black text-[#0B3D2E]">
            {t('nav_lots')} ({lots.length})
          </h2>
        </div>

        <button
          onClick={() => navigate('/add-scrap')}
          className="flex items-center gap-1 text-xs font-bold text-[#14634A] hover:underline cursor-pointer"
        >
          <Plus size={15} />
          <span>{t('btn_new_lot')}</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        {(['all', 'active', 'completed'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold capitalize transition-colors cursor-pointer ${
              filter === f
                ? 'bg-[#0B3D2E] text-white'
                : 'bg-white border border-[#E3E0D5] text-[#5B6B62] hover:bg-[#F7F5EF]'
            }`}
          >
            {t(`filter_${f}`)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="p-6 text-center text-xs text-[#5B6B62]">{t('loading_lots')}</div>
      ) : filtered.length === 0 ? (
        <div className="p-8 text-center text-xs text-[#5B6B62] bg-white rounded-2xl border border-[#E3E0D5]">
          {t('no_lots_found')}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((lot) => (
            <LotCard
              key={lot.id}
              id={lot.id}
              lotCode={lot.lot_code}
              status={lot.status}
              estMinPaise={lot.est_total_min_paise}
              estMaxPaise={lot.est_total_max_paise}
              finalPaise={lot.final_amount_paise}
              weightGrams={lot.actual_total_weight_g || lot.est_total_weight_g}
              isHazardous={lot.is_hazardous}
              itemCount={lot.items.length}
              createdAt={lot.created_at}
            />
          ))}
        </div>
      )}
    </div>
  );
};
