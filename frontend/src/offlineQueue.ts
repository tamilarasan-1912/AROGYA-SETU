import Dexie, { Table } from 'dexie';

type SyncOperation = { id?: number; operation_id: string; endpoint: string; payload: unknown; created_at: string; synced: number };

class OfflineDB extends Dexie {
  operations!: Table<SyncOperation, number>;
  constructor() {
    super('arogyasetu-offline');
    this.version(1).stores({ operations: '++id, operation_id, synced, created_at' });
  }
}

export const offlineDB = new OfflineDB();

export async function enqueue(endpoint: string, payload: unknown) {
  const operation_id = crypto.randomUUID();
  await offlineDB.operations.add({ operation_id, endpoint, payload, created_at: new Date().toISOString(), synced: 0 });
  return operation_id;
}

export async function flushQueue(apiBase: string) {
  if (!navigator.onLine) return { synced: 0, remaining: await offlineDB.operations.where('synced').equals(0).count() };
  const pending = await offlineDB.operations.where('synced').equals(0).toArray();
  let synced = 0;
  for (const item of pending) {
    try {
      const response = await fetch(`${apiBase}${item.endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ operation_id: item.operation_id, payload: item.payload }) });
      if (response.ok) { await offlineDB.operations.update(item.id!, { synced: 1 }); synced += 1; }
    } catch { break; }
  }
  return { synced, remaining: pending.length - synced };
}
