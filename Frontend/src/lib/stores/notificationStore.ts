import { writable } from 'svelte/store';

export type Notification = {
  id: string;
  title: string;
  time: string;
};

function createNotificationStore() {
  const { subscribe, update, set } = writable<Notification[]>([]);

  return {
    subscribe,
    push: (title: string) => {
      const n: Notification = { id: crypto.randomUUID(), title, time: 'Just now' };
      update(list => [n, ...list].slice(0, 50));
    },
    clear: () => set([])
  };
}

export const notificationStore = createNotificationStore();






















