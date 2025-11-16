import { defineStore } from 'pinia';

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
  }),
  actions: {
    setUser(user) {
      this.user = user;
    },
    setLoading(loading) {
      this.loading = loading;
    },
    setError(error) {
      this.error = error;
    },
  },
});
