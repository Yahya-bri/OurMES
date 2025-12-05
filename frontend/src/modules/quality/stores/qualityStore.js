/**
 * Quality Store
 *
 * Centralized state management for quality operations.
 */
import { defineStore } from 'pinia';
import {
  getInspectionConfigs,
  getQualityChecks,
  recordQualityCheck,
  getPassRate,
  getNCRs,
  createNCR,
  changeNCRStatus,
  closeNCR,
  getNCRStats,
  getSPCData,
  getSPCStats,
  getSPCControlChart,
} from '../services/qualityService';

export const useQualityStore = defineStore('quality', {
  state: () => ({
    // Data
    inspectionConfigs: [],
    qualityChecks: [],
    ncrs: [],
    spcData: [],
    // Stats
    ncrStats: {
      total: 0,
      quarantine: 0,
      review: 0,
      closed: 0,
    },
    passRate: null,
    spcStats: null,
    controlChartData: null,
    // UI State
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get inspection configs by operation.
     */
    configsByOperation: (state) => (operationId) => {
      return state.inspectionConfigs.filter((c) => c.operation === operationId);
    },

    /**
     * Get quality checks by order.
     */
    checksByOrder: (state) => (orderNumber) => {
      return state.qualityChecks.filter((c) => c.order_number === orderNumber);
    },

    /**
     * Get open NCRs.
     */
    openNCRs: (state) => {
      return state.ncrs.filter((n) => n.status !== 'closed');
    },

    /**
     * Get failed quality checks.
     */
    failedChecks: (state) => {
      return state.qualityChecks.filter((c) => !c.passed);
    },
  },

  actions: {
    // ==================== INSPECTION CONFIGS ====================

    async fetchInspectionConfigs(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getInspectionConfigs(params);
        this.inspectionConfigs = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // ==================== QUALITY CHECKS ====================

    async fetchQualityChecks(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getQualityChecks(params);
        this.qualityChecks = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async recordCheck(configId, orderNumber, resultValue, inspectorName) {
      this.loading = true;
      try {
        const data = await recordQualityCheck(configId, orderNumber, resultValue, inspectorName);
        this.qualityChecks.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchPassRate(configId = null, days = 30) {
      try {
        const data = await getPassRate(configId, days);
        this.passRate = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    // ==================== NCR ====================

    async fetchNCRs(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getNCRs(params);
        this.ncrs = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addNCR(ncrData) {
      this.loading = true;
      try {
        const data = await createNCR(ncrData);
        this.ncrs.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async changeStatus(id, newStatus) {
      try {
        const data = await changeNCRStatus(id, newStatus);
        const index = this.ncrs.findIndex((n) => n.id === id);
        if (index !== -1) this.ncrs[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async closeNCRWithDisposition(id, disposition = null) {
      try {
        const data = await closeNCR(id, disposition);
        const index = this.ncrs.findIndex((n) => n.id === id);
        if (index !== -1) this.ncrs[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async fetchNCRStats() {
      try {
        const data = await getNCRStats();
        this.ncrStats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    // ==================== SPC ====================

    async fetchSPCData(params = {}) {
      this.loading = true;
      try {
        const data = await getSPCData(params);
        this.spcData = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchSPCStats(parameterName, limit = 100) {
      try {
        const data = await getSPCStats(parameterName, limit);
        this.spcStats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async fetchControlChart(parameterName, limit = 50) {
      try {
        const data = await getSPCControlChart(parameterName, limit);
        this.controlChartData = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },
  },
});

export default useQualityStore;
