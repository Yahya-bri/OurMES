/**
 * Production Store
 *
 * Centralized state management for production counting and operator console.
 * Handles production records, active operations, and performance metrics.
 */
import { defineStore } from 'pinia';
import {
  getProductionRecords,
  getProductionRecord,
  createProductionRecord,
  updateProductionRecord,
  startProduction,
  completeProduction,
  getOrderProgress,
  getWorkstationPerformance,
} from '../services/productionCountingService';

export const useProductionStore = defineStore('production', {
  state: () => ({
    // Data
    records: [],
    currentRecord: null,
    activeRecords: [],
    orderProgress: {},
    workstationPerformance: {},
    // UI State
    loading: false,
    starting: false,
    completing: false,
    error: null,
    // Operator Console State
    selectedWorkstation: null,
    selectedOperator: null,
    selectedProductionLine: null,
  }),

  getters: {
    /**
     * Get records for a specific order.
     */
    recordsByOrder: (state) => (orderId) => {
      return state.records.filter((record) => record.order === orderId);
    },

    /**
     * Get records for a specific workstation.
     */
    recordsByWorkstation: (state) => (workstationId) => {
      return state.records.filter((record) => record.workstation === workstationId);
    },

    /**
     * Get active (in_progress) records.
     */
    inProgressRecords: (state) => {
      return state.records.filter((record) => record.status === 'in_progress');
    },

    /**
     * Check if there's an active record for current workstation.
     */
    hasActiveRecord: (state) => {
      if (!state.selectedWorkstation) return false;
      return state.activeRecords.some(
        (record) => record.workstation === state.selectedWorkstation && record.status === 'in_progress'
      );
    },

    /**
     * Get current active record for selected workstation.
     */
    currentActiveRecord: (state) => {
      if (!state.selectedWorkstation) return null;
      return state.activeRecords.find(
        (record) => record.workstation === state.selectedWorkstation && record.status === 'in_progress'
      );
    },
  },

  actions: {
    /**
     * Fetch production records.
     */
    async fetchRecords(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getProductionRecords(params);
        this.records = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch a single record.
     */
    async fetchRecord(id) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getProductionRecord(id);
        this.currentRecord = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch active records for a workstation.
     */
    async fetchActiveRecords(workstationId) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getProductionRecords({
          workstation: workstationId,
          status: 'in_progress',
        });
        this.activeRecords = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Start production for an order/operation.
     */
    async startProductionRecord(recordData) {
      this.starting = true;
      this.error = null;
      try {
        const data = await startProduction(recordData);
        this.records.unshift(data);
        this.activeRecords.push(data);
        this.currentRecord = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.starting = false;
      }
    },

    /**
     * Record output quantities.
     */
    async recordOutput(id, quantities) {
      this.loading = true;
      this.error = null;
      try {
        const data = await updateProductionRecord(id, quantities);
        // Update in records list
        const index = this.records.findIndex((r) => r.id === id);
        if (index !== -1) {
          this.records[index] = data;
        }
        // Update in active records
        const activeIndex = this.activeRecords.findIndex((r) => r.id === id);
        if (activeIndex !== -1) {
          this.activeRecords[activeIndex] = data;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Complete production record.
     */
    async completeProductionRecord(id, finalData = {}) {
      this.completing = true;
      this.error = null;
      try {
        const data = await completeProduction(id, finalData);
        // Update in records list
        const index = this.records.findIndex((r) => r.id === id);
        if (index !== -1) {
          this.records[index] = data;
        }
        // Remove from active records
        this.activeRecords = this.activeRecords.filter((r) => r.id !== id);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.completing = false;
      }
    },

    /**
     * Fetch order progress.
     */
    async fetchOrderProgress(orderId) {
      try {
        const data = await getOrderProgress(orderId);
        this.orderProgress[orderId] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    /**
     * Fetch workstation performance.
     */
    async fetchWorkstationPerformance(workstationId, days = 7) {
      try {
        const data = await getWorkstationPerformance(workstationId, days);
        this.workstationPerformance[workstationId] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    /**
     * Set selected workstation for operator console.
     */
    setSelectedWorkstation(workstationId) {
      this.selectedWorkstation = workstationId;
      if (workstationId) {
        this.fetchActiveRecords(workstationId);
      }
    },

    /**
     * Set selected operator.
     */
    setSelectedOperator(operatorId) {
      this.selectedOperator = operatorId;
    },

    /**
     * Set selected production line.
     */
    setSelectedProductionLine(lineId) {
      this.selectedProductionLine = lineId;
    },

    /**
     * Clear selection.
     */
    clearSelection() {
      this.selectedWorkstation = null;
      this.selectedOperator = null;
      this.selectedProductionLine = null;
      this.activeRecords = [];
      this.currentRecord = null;
    },
  },
});

export default useProductionStore;
