import Dexie, { Table } from 'dexie';

type SyncOperation = {
  id?: number;
  operation_id: string;
  endpoint: string;
  entity_type: string;
  entity_id?: string;
  payload: unknown;
  created_at: string;
  synced: number;
};

export type PulledOperation = {
  operation_id: string;
  device_id: string;
  entity_type: string;
  entity_id?: string;
  payload: Record<string, unknown>;
  status: string;
  created_at?: string;
};

class OfflineDB extends Dexie {
  operations!: Table<SyncOperation, number>;
  constructor() {
    super('arogyasetu-offline');
    this.version(2).stores({ operations: '++id, operation_id, synced, created_at, entity_type' });
  }
}

export const offlineDB = new OfflineDB();

export async function enqueue(endpoint: string, payload: unknown, entity_type = 'unknown', entity_id?: string) {
  const operation_id = crypto.randomUUID();
  await offlineDB.operations.add({ operation_id, endpoint, entity_type, entity_id, payload, created_at: new Date().toISOString(), synced: 0 });
  return operation_id;
}

export async function pendingCount() {
  return offlineDB.operations.where('synced').equals(0).count();
}

export async function flushQueue(apiBase: string, deviceId = 'web-device') {
  if (!navigator.onLine) return { synced: 0, remaining: await pendingCount() };
  const pending = await offlineDB.operations.where('synced').equals(0).sortBy('created_at');
  let synced = 0;
  for (const item of pending) {
    try {
      const response = await fetch(`${apiBase}/sync/push`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ operation_id: item.operation_id, device_id: deviceId, entity_type: item.entity_type, entity_id: item.entity_id, payload: item.payload }) });
      if (!response.ok) break;
      await offlineDB.operations.update(item.id!, { synced: 1 });
      synced += 1;
    } catch { break; }
  }
  return { synced, remaining: await pendingCount() };
}

export async function pullRemoteOperations(apiBase: string, deviceId = 'web-device') {
  if (!navigator.onLine) return [] as PulledOperation[];
  const response = await fetch(`${apiBase}/sync/pull?device_id=${encodeURIComponent(deviceId)}`);
  if (!response.ok) throw new Error(`Sync pull failed: ${response.status}`);
  const body = await response.json();
  return (body.operations || []) as PulledOperation[];
}

export async function syncNow(apiBase: string, deviceId = 'web-device') {
  const pushed = await flushQueue(apiBase, deviceId);
  const pulled = await pullRemoteOperations(apiBase, deviceId);
  return { ...pushed, pulled };
}

export function registerOnlineSync(apiBase: string, deviceId = 'web-device', onComplete?: (result: Awaited<ReturnType<typeof syncNow>>) => void) {
  const run = async () => {
    try { onComplete?.(await syncNow(apiBase, deviceId)); } catch { /* Preserve queue for retry. */ }
  };
  window.addEventListener('online', run);
  if (navigator.onLine) void run();
  return () => window.removeEventListener('online', run);
}
