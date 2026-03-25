import { create } from 'zustand';
import { fetchEvents as apiFetchEvents } from '../api.js';

const STALE_MS = 60_000;

const useEventsStore = create((set, get) => ({
  events: [],
  loading: false,
  lastFetched: null,

  fetchEvents: async () => {
    const { lastFetched, loading } = get();
    if (loading) return;
    if (lastFetched && Date.now() - lastFetched < STALE_MS) return;

    set({ loading: true });
    try {
      const events = await apiFetchEvents();
      set({ events, loading: false, lastFetched: Date.now() });
    } catch {
      set({ loading: false });
    }
  },
}));

export default useEventsStore;
