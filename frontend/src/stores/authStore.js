import { create } from 'zustand';
import { login as apiLogin, logout as apiLogout, fetchMe } from '../api.js';

let checkAuthPromise = null;

const useAuthStore = create((set, get) => ({
  user: null,
  loading: true,
  initialized: false,

  checkAuth: async () => {
    if (get().initialized) return get().user;
    if (checkAuthPromise) return checkAuthPromise;
    checkAuthPromise = fetchMe()
      .then((user) => {
        set({ user, loading: false, initialized: true });
        return user;
      })
      .catch(() => {
        set({ user: null, loading: false, initialized: true });
        return null;
      })
      .finally(() => {
        checkAuthPromise = null;
      });
    set({ loading: true });
    return checkAuthPromise;
  },

  login: async (username, password) => {
    const user = await apiLogin(username, password);
    set({ user, initialized: true });
    return user;
  },

  logout: async () => {
    await apiLogout();
    set({ user: null, initialized: false });
  },
}));

export default useAuthStore;
