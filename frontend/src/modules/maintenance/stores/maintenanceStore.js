/**
 * Maintenance Store
 *
 * Centralized state management for maintenance operations.
 */
import { defineStore } from 'pinia';
import {
  getMaintenanceLogs,
  getMaintenanceLog,
  createMaintenanceLog,
  updateMaintenanceLog,
  deleteMaintenanceLog,
  startMaintenance,
  completeMaintenance,
  getWorkstationDowntime,
  getMaintenanceStats,
  getBreakdownFrequency,
  getActiveMaintenance,
} from '../services/maintenanceService';

export const useMaintenanceStore = defineStore('maintenance', {
  state: () => ({
    // Data
    logs: [],
    activeLogs: [],
    currentLog: null,
    // Stats
    stats: {
      total: 0,
      active: 0,
      preventive: 0,
      corrective: 0,
      breakdown: 0,
    },
    downtimeData: {},
    breakdownFrequency: [],
    // UI State
    loading: false,
    error: null,
  }),

  getters: {
    /**
     * Get logs by workstation.
     */
    logsByWorkstation: (state) => (workstationId) => {
      return state.logs.filter((log) => log.workstation === workstationId);
    },

    /**
     * Get logs by type.
     */
    logsByType: (state) => (type) => {
      return state.logs.filter((log) => log.type === type);
    },

    /**
     * Get active (ongoing) maintenance logs.
     */
    ongoingMaintenance: (state) => {
      return state.logs.filter((log) => !log.end_time);
    },

    /**
     * Check if workstation is under maintenance.
     */
    isWorkstationUnderMaintenance: (state) => (workstationId) => {
      return state.activeLogs.some(
        (log) => log.workstation === workstationId && !log.end_time
      );
    },
  },

  actions: {
    async fetchLogs(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getMaintenanceLogs(params);
        this.logs = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchLog(id) {
      this.loading = true;
      try {
        const data = await getMaintenanceLog(id);
        this.currentLog = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchActiveLogs() {
      this.loading = true;
      try {
        const data = await getActiveMaintenance();
        this.activeLogs = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addLog(logData) {
      this.loading = true;
      try {
        const data = await createMaintenanceLog(logData);
        this.logs.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async modifyLog(id, logData) {
      this.loading = true;
      try {
        const data = await updateMaintenanceLog(id, logData);
        const index = this.logs.findIndex((log) => log.id === id);
        if (index !== -1) this.logs[index] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async removeLog(id) {
      this.loading = true;
      try {
        await deleteMaintenanceLog(id);
        this.logs = this.logs.filter((log) => log.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async startMaintenanceActivity(workstationId, type, description, technicianName) {
      this.loading = true;
      try {
        const data = await startMaintenance(workstationId, type, description, technicianName);
        this.logs.unshift(data);
        this.activeLogs.push(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async completeMaintenanceActivity(id, notes = '') {
      this.loading = true;
      try {
        const data = await completeMaintenance(id, notes);
        const index = this.logs.findIndex((log) => log.id === id);
        if (index !== -1) this.logs[index] = data;
        // Remove from active logs
        this.activeLogs = this.activeLogs.filter((log) => log.id !== id);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchWorkstationDowntime(workstationId, days = 30) {
      try {
        const data = await getWorkstationDowntime(workstationId, days);
        this.downtimeData[workstationId] = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async fetchStats() {
      try {
        const data = await getMaintenanceStats();
        this.stats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    async fetchBreakdownFrequency(workstationId = null, days = 90) {
      try {
        const data = await getBreakdownFrequency(workstationId, days);
        this.breakdownFrequency = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },
  },
});

export default useMaintenanceStore;
