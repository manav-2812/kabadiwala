import { getDB } from './db';

export async function queueAction(action: string, payload: any): Promise<string> {
  const db = await getDB();
  const client_uuid = `outbox-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  await db.put('outbox', {
    client_uuid,
    action,
    payload,
    timestamp: Date.now()
  });
  return client_uuid;
}

export async function getQueuedActions() {
  const db = await getDB();
  return db.getAll('outbox');
}

export async function removeQueuedAction(client_uuid: string) {
  const db = await getDB();
  return db.delete('outbox', client_uuid);
}

export async function clearOutbox() {
  const db = await getDB();
  return db.clear('outbox');
}
