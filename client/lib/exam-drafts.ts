function openDrafts(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("evaly-exam-drafts", 1);
    request.onupgradeneeded = () => request.result.createObjectStore("drafts");
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function readDraft<T>(key: string): Promise<T | undefined> {
  const db = await openDrafts();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("drafts", "readonly");
    const request = transaction.objectStore("drafts").get(key);
    transaction.oncomplete = () => { db.close(); resolve(request.result); };
    transaction.onerror = () => { db.close(); reject(transaction.error); };
  });
}

export async function writeDraft(key: string, value: unknown): Promise<void> {
  const db = await openDrafts();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("drafts", "readwrite");
    if (value === undefined) transaction.objectStore("drafts").delete(key);
    else transaction.objectStore("drafts").put(value, key);
    transaction.oncomplete = () => { db.close(); resolve(); };
    transaction.onabort = transaction.onerror = () => { db.close(); reject(transaction.error); };
  });
}

export async function listDrafts<T>(prefix: string): Promise<Array<{ key: string; value: T }>> {
  const db = await openDrafts();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction("drafts", "readonly");
    const request = transaction.objectStore("drafts").openCursor();
    const rows: Array<{ key: string; value: T }> = [];
    request.onsuccess = () => {
      const cursor = request.result;
      if (!cursor) return;
      const key = String(cursor.key);
      if (key.startsWith(prefix)) rows.push({ key, value: cursor.value as T });
      cursor.continue();
    };
    transaction.oncomplete = () => { db.close(); resolve(rows); };
    transaction.onerror = () => { db.close(); reject(transaction.error); };
  });
}
