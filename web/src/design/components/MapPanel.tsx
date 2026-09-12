import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useOfflineStore } from '../../features/offline/offlineStore';
import { MapPin, Navigation } from 'lucide-react';

interface MapMarker {
  id: string;
  lat: number;
  lng: number;
  title: string;
  subtitle?: string;
  isHazardous?: boolean;
  isAgent?: boolean;
}

interface MapPanelProps {
  markers: MapMarker[];
  center?: [number, number];
  zoom?: number;
  height?: string;
  onMarkerClick?: (id: string) => void;
}

export const MapPanel: React.FC<MapPanelProps> = ({
  markers,
  center = [28.6139, 77.2090], // Default Delhi
  zoom = 12,
  height = '320px',
  onMarkerClick
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const { isSimulatedOffline, isOnline } = useOfflineStore();

  const isActuallyOffline = isSimulatedOffline || !isOnline;

  useEffect(() => {
    if (!mapContainerRef.current || isActuallyOffline) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center,
        zoom,
        zoomControl: false
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      L.control.zoom({ position: 'bottomright' }).addTo(map);
      mapInstanceRef.current = map;
    } else {
      mapInstanceRef.current.setView(center, zoom);
    }

    const map = mapInstanceRef.current;

    // Clear previous markers
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.CircleMarker) {
        map.removeLayer(layer);
      }
    });

    // Add markers
    markers.forEach((m) => {
      const color = m.isAgent ? '#2F6FDE' : (m.isHazardous ? '#D64545' : '#14634A');
      const circle = L.circleMarker([m.lat, m.lng], {
        radius: m.isAgent ? 10 : 8,
        fillColor: color,
        color: '#FFFFFF',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(map);

      circle.bindPopup(`<b>${m.title}</b><br/>${m.subtitle || ''}`);
      if (onMarkerClick) {
        circle.on('click', () => onMarkerClick(m.id));
      }
    });

    return () => {
      // Keep map alive for performance or clean up if unmounting
    };
  }, [markers, center, zoom, isActuallyOffline]);

  if (isActuallyOffline) {
    return (
      <div
        style={{ height }}
        className="w-full bg-[#F7F5EF] border border-[#E3E0D5] rounded-2xl p-4 flex flex-col gap-3 overflow-y-auto"
      >
        <div className="flex items-center gap-2 text-xs font-bold text-[#5B6B62] uppercase tracking-wider">
          <Navigation size={14} />
          <span>Offline List View (Map Tiles Cached Offline)</span>
        </div>
        <div className="flex flex-col gap-2">
          {markers.map((m) => (
            <div
              key={m.id}
              onClick={() => onMarkerClick?.(m.id)}
              className="p-3 bg-white rounded-xl border border-[#E3E0D5] flex items-center justify-between cursor-pointer hover:border-[#14634A]"
            >
              <div className="flex items-center gap-2">
                <MapPin size={16} className={m.isHazardous ? 'text-[#D64545]' : 'text-[#14634A]'} />
                <div>
                  <h5 className="text-sm font-bold text-[#0B3D2E]">{m.title}</h5>
                  <p className="text-xs text-[#5B6B62]">{m.subtitle || 'Verified scrap location'}</p>
                </div>
              </div>
              <span className="text-xs text-[#14634A] font-semibold">View</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={mapContainerRef}
      style={{ height }}
      className="w-full rounded-2xl border border-[#E3E0D5] overflow-hidden shadow-xs z-0"
    />
  );
};
