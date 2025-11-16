import { defineStore } from 'pinia';
import { login as apiLogin, getMe } from '../services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    roles: [],
    loading: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    hasRole: (state) => (roles) => roles.some((r) => state.roles.includes(r)),
  },
  actions: {
    async login(username, password) {
      this.loading = true;
      try {
        const { access } = await apiLogin(username, password);
        this.token = access;
        localStorage.setItem('token', access);
        await this.fetchMe();
        this.error = null;
        return true;
      } catch (e) {
        this.error = 'Invalid credentials';
        this.logout();
        return false;
      } finally {
        this.loading = false;
      }
    },
    async fetchMe() {
      try {
        const me = await getMe();
        this.user = me;
        this.roles = me.roles || [];
      } catch (e) {
        this.logout();
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      this.roles = [];
      localStorage.removeItem('token');
    },
  },
});
