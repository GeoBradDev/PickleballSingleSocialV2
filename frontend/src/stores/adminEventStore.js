import { create } from 'zustand';
import {
  fetchEventStats,
  fetchEventRegistrations,
  fetchEventMatches,
  fetchEventMatchSubmissions,
  triggerCommand as apiTriggerCommand,
} from '../api.js';

let loadEventPromise = null;

const useAdminEventStore = create((set, get) => ({
  stats: null,
  registrations: [],
  matches: [],
  submissions: [],
  loading: true,
  matchesLoading: false,
  matchesLoaded: false,
  submissionsLoading: false,
  submissionsLoaded: false,
  commandLoading: false,
  commandAlert: null,
  activeTab: 0,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setCommandAlert: (alert) => set({ commandAlert: alert }),

  loadEvent: async (eventId) => {
    if (loadEventPromise) return loadEventPromise;
    set({ loading: true });
    loadEventPromise = Promise.all([
      fetchEventStats(eventId),
      fetchEventRegistrations(eventId),
    ])
      .then(([stats, registrations]) => {
        set({ stats, registrations, loading: false });
      })
      .catch(() => {
        set({ loading: false });
      })
      .finally(() => {
        loadEventPromise = null;
      });
    return loadEventPromise;
  },

  loadMatches: async (eventId) => {
    if (get().matchesLoaded || get().matchesLoading) return;
    set({ matchesLoading: true });
    try {
      const matches = await fetchEventMatches(eventId);
      set({ matches, matchesLoaded: true, matchesLoading: false });
    } catch {
      set({ matches: [], matchesLoading: false });
    }
  },

  loadSubmissions: async (eventId) => {
    if (get().submissionsLoaded || get().submissionsLoading) return;
    set({ submissionsLoading: true });
    try {
      const submissions = await fetchEventMatchSubmissions(eventId);
      set({ submissions, submissionsLoaded: true, submissionsLoading: false });
    } catch {
      set({ submissions: [], submissionsLoading: false });
    }
  },

  triggerCommand: async (eventId, command) => {
    set({ commandLoading: true, commandAlert: null });
    try {
      const result = await apiTriggerCommand(eventId, command);
      set({
        commandLoading: false,
        commandAlert: {
          severity: 'success',
          message: result.message || `${command} completed successfully.`,
        },
      });
      // Refresh matches and submissions after command
      const matches = await fetchEventMatches(eventId).catch(() => get().matches);
      const submissions = await fetchEventMatchSubmissions(eventId).catch(() => get().submissions);
      set({ matches, matchesLoaded: true, submissions, submissionsLoaded: true });
    } catch (err) {
      set({
        commandLoading: false,
        commandAlert: {
          severity: 'error',
          message: err.message || `${command} failed.`,
        },
      });
    }
  },

  reset: () =>
    set({
      stats: null,
      registrations: [],
      matches: [],
      submissions: [],
      loading: true,
      matchesLoading: false,
      matchesLoaded: false,
      submissionsLoading: false,
      submissionsLoaded: false,
      commandLoading: false,
      commandAlert: null,
      activeTab: 0,
    }),
}));

export default useAdminEventStore;
