import { defineStore } from 'pinia';
import { getRoutings, getRouting, createRouting, updateRouting, deleteRouting, changeRoutingState } from '../services/routingService';

export const useRoutingStore = defineStore('routing', {
  state: () => ({
    routings: [],
    currentRouting: null,
    loading: false,
    error: null,
  }),
  
  actions: {
    async fetchRoutings(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getRoutings(params);
        this.routings = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchRouting(id) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getRouting(id);
        this.currentRouting = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async addRouting(routingData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await createRouting(routingData);
        this.routings.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async modifyRouting(id, routingData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await updateRouting(id, routingData);
        const index = this.routings.findIndex(t => t.id === id);
        if (index !== -1) {
          this.routings[index] = data;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async removeRouting(id) {
      this.loading = true;
      this.error = null;
      try {
        await deleteRouting(id);
        this.routings = this.routings.filter(t => t.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async updateRoutingState(id, state) {
      this.loading = true;
      this.error = null;
      try {
        const data = await changeRoutingState(id, state);
        const index = this.routings.findIndex(t => t.id === id);
        if (index !== -1) {
          this.routings[index].state = state;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
