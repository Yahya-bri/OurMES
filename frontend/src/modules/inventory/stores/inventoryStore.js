/**
 * Inventory Store
 *
 * Centralized state management for inventory operations.
 */
import { defineStore } from 'pinia';
import {
  getStocks,
  getStock,
  createStock,
  updateStock,
  deleteStock,
  adjustStock,
  transferStock,
  getContainers,
  getKanbanCards,
  getKanbanStats,
  triggerReplenishment,
  completeReplenishment,
  getTraceabilityRecords,
  traceForward,
  traceBackward,
} from '../services/inventoryService';

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    // Data
    stocks: [],
    containers: [],
    kanbanCards: [],
    traceabilityRecords: [],
    // Current items
    currentStock: null,
    // Stats
    kanbanStats: {
      total: 0,
      full: 0,
      replenishing: 0,
      empty: 0,
    },
    // Traceability results
    traceResults: null,
    // UI State
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get stocks by material.
     */
    stocksByMaterial: (state) => (materialId) => {
      return state.stocks.filter((s) => s.material === materialId);
    },

    /**
     * Get stocks by location.
     */
    stocksByLocation: (state) => (location) => {
      return state.stocks.filter((s) => s.location_name === location);
    },

    /**
     * Get low stock items.
     */
    lowStockItems: (state) => {
      return state.stocks.filter((s) => parseFloat(s.quantity) <= 0);
    },

    /**
     * Get kanban cards needing replenishment.
     */
    cardsNeedingReplenishment: (state) => {
      return state.kanbanCards.filter((c) => c.status !== 'full');
    },
  },

  actions: {
    // ==================== STOCKS ====================

    async fetchStocks(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getStocks(params);
        this.stocks = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchStock(id) {
      this.loading = true;
      try {
        const data = await getStock(id);
        this.currentStock = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addStock(stockData) {
      this.loading = true;
      try {
        const data = await createStock(stockData);
        this.stocks.push(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async modifyStock(id, stockData) {
      this.loading = true;
      try {
        const data = await updateStock(id, stockData);
        const index = this.stocks.findIndex((s) => s.id === id);
        if (index !== -1) this.stocks[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async removeStock(id) {
      this.loading = true;
      try {
        await deleteStock(id);
        this.stocks = this.stocks.filter((s) => s.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async adjustStockQuantity(id, change, reason) {
      this.loading = true;
      try {
        const data = await adjustStock(id, change, reason);
        const index = this.stocks.findIndex((s) => s.id === id);
        if (index !== -1) this.stocks[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async transferStockBetweenLocations(materialId, fromLoc, toLoc, qty) {
      this.loading = true;
      try {
        const data = await transferStock(materialId, fromLoc, toLoc, qty);
        await this.fetchStocks(); // Refresh stocks
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ==================== CONTAINERS ====================

    async fetchContainers(params = {}) {
      this.loading = true;
      try {
        const data = await getContainers(params);
        this.containers = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ==================== KANBAN ====================

    async fetchKanbanCards(params = {}) {
      this.loading = true;
      try {
        const data = await getKanbanCards(params);
        this.kanbanCards = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchKanbanStats() {
      try {
        const data = await getKanbanStats();
        this.kanbanStats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async triggerKanbanReplenishment(id) {
      try {
        const data = await triggerReplenishment(id);
        const index = this.kanbanCards.findIndex((c) => c.id === id);
        if (index !== -1) this.kanbanCards[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async completeKanbanReplenishment(id) {
      try {
        const data = await completeReplenishment(id);
        const index = this.kanbanCards.findIndex((c) => c.id === id);
        if (index !== -1) this.kanbanCards[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    // ==================== TRACEABILITY ====================

    async fetchTraceabilityRecords(params = {}) {
      this.loading = true;
      try {
        const data = await getTraceabilityRecords(params);
        this.traceabilityRecords = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async traceForwardFromBatch(batch) {
      this.loading = true;
      try {
        const data = await traceForward(batch);
        this.traceResults = { type: 'forward', batch, data };
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async traceBackwardFromBatch(batch) {
      this.loading = true;
      try {
        const data = await traceBackward(batch);
        this.traceResults = { type: 'backward', batch, data };
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    clearTraceResults() {
      this.traceResults = null;
    },
  },
});

export default useInventoryStore;
