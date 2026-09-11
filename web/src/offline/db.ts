import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface KabadiwalaDB extends DBSchema {
  outbox: {
    key: string;
    value: {
      client_uuid: string;
      action: string;
      payload: any;
      timestamp: number;
    };
  };
  basket: {
    key: string;
    value: {
      id: string;
      material_id: string;
      material_code: string;
      weight_g: number;
      condition: string;
      photo_data?: string;
      timestamp: number;
    };
  };
  cache: {
    key: string;
    value: {
      key: string;
      data: any;
      cached_at: number;
    };
  };
}

const DB_NAME = 'kabadiwala_offline_db';
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<KabadiwalaDB>> | null = null;

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<KabadiwalaDB>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('outbox')) {
          db.createObjectStore('outbox', { keyPath: 'client_uuid' });
        }
        if (!db.objectStoreNames.contains('basket')) {
          db.createObjectStore('basket', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache', { keyPath: 'key' });
        }
      }
    });
  }
  return dbPromise;
}
