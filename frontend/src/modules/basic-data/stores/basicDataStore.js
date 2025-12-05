/**
 * Basic Data Store
 *
 * Centralized state management for master data entities:
 * workstations, production lines, companies, and staff.
 */
import { defineStore } from 'pinia';
import {
  getWorkstations,
  getWorkstation,
  createWorkstation,
  updateWorkstation,
  deleteWorkstation,
  getProductionLines,
  getProductionLine,
  createProductionLine,
  updateProductionLine,
  deleteProductionLine,
  getCompanies,
  getCompany,
  createCompany,
  updateCompany,
  deleteCompany,
  getStaff,
  getStaffMember,
  createStaffMember,
  updateStaffMember,
  deleteStaffMember,
} from '../services/basicDataService';

export const useBasicDataStore = defineStore('basicData', {
  state: () => ({
    // Data
    workstations: [],
    productionLines: [],
    companies: [],
    staff: [],
    // Current items
    currentWorkstation: null,
    currentProductionLine: null,
    currentCompany: null,
    currentStaffMember: null,
    // UI State
    loading: {
      workstations: false,
      productionLines: false,
      companies: false,
      staff: false,
    },
    error: null,
  }),

  getters: {
    /**
     * Get active workstations.
     */
    activeWorkstations: (state) => {
      return state.workstations.filter((ws) => ws.active);
    },

    /**
     * Get workstations by production line.
     */
    workstationsByLine: (state) => (lineId) => {
      return state.workstations.filter((ws) => ws.production_line === lineId);
    },

    /**
     * Get active production lines.
     */
    activeProductionLines: (state) => {
      return state.productionLines.filter((line) => line.active);
    },

    /**
     * Get active companies.
     */
    activeCompanies: (state) => {
      return state.companies.filter((company) => company.active);
    },

    /**
     * Get active staff.
     */
    activeStaff: (state) => {
      return state.staff.filter((member) => member.active);
    },

    /**
     * Check if any data is loading.
     */
    isLoading: (state) => {
      return Object.values(state.loading).some((v) => v);
    },
  },

  actions: {
    // ==================== WORKSTATIONS ====================

    async fetchWorkstations(params = {}) {
      this.loading.workstations = true;
      this.error = null;
      try {
        const data = await getWorkstations(params);
        this.workstations = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.workstations = false;
      }
    },

    async fetchWorkstation(id) {
      this.loading.workstations = true;
      try {
        const data = await getWorkstation(id);
        this.currentWorkstation = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.workstations = false;
      }
    },

    async addWorkstation(data) {
      this.loading.workstations = true;
      try {
        const result = await createWorkstation(data);
        this.workstations.push(result);
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.workstations = false;
      }
    },

    async modifyWorkstation(id, data) {
      this.loading.workstations = true;
      try {
        const result = await updateWorkstation(id, data);
        const index = this.workstations.findIndex((ws) => ws.id === id);
        if (index !== -1) this.workstations[index] = result;
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.workstations = false;
      }
    },

    async removeWorkstation(id) {
      this.loading.workstations = true;
      try {
        await deleteWorkstation(id);
        this.workstations = this.workstations.filter((ws) => ws.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.workstations = false;
      }
    },

    // ==================== PRODUCTION LINES ====================

    async fetchProductionLines(params = {}) {
      this.loading.productionLines = true;
      this.error = null;
      try {
        const data = await getProductionLines(params);
        this.productionLines = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.productionLines = false;
      }
    },

    async fetchProductionLine(id) {
      this.loading.productionLines = true;
      try {
        const data = await getProductionLine(id);
        this.currentProductionLine = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.productionLines = false;
      }
    },

    async addProductionLine(data) {
      this.loading.productionLines = true;
      try {
        const result = await createProductionLine(data);
        this.productionLines.push(result);
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.productionLines = false;
      }
    },

    async modifyProductionLine(id, data) {
      this.loading.productionLines = true;
      try {
        const result = await updateProductionLine(id, data);
        const index = this.productionLines.findIndex((line) => line.id === id);
        if (index !== -1) this.productionLines[index] = result;
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.productionLines = false;
      }
    },

    async removeProductionLine(id) {
      this.loading.productionLines = true;
      try {
        await deleteProductionLine(id);
        this.productionLines = this.productionLines.filter((line) => line.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.productionLines = false;
      }
    },

    // ==================== COMPANIES ====================

    async fetchCompanies(params = {}) {
      this.loading.companies = true;
      this.error = null;
      try {
        const data = await getCompanies(params);
        this.companies = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.companies = false;
      }
    },

    async fetchCompany(id) {
      this.loading.companies = true;
      try {
        const data = await getCompany(id);
        this.currentCompany = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.companies = false;
      }
    },

    async addCompany(data) {
      this.loading.companies = true;
      try {
        const result = await createCompany(data);
        this.companies.push(result);
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.companies = false;
      }
    },

    async modifyCompany(id, data) {
      this.loading.companies = true;
      try {
        const result = await updateCompany(id, data);
        const index = this.companies.findIndex((c) => c.id === id);
        if (index !== -1) this.companies[index] = result;
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.companies = false;
      }
    },

    async removeCompany(id) {
      this.loading.companies = true;
      try {
        await deleteCompany(id);
        this.companies = this.companies.filter((c) => c.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.companies = false;
      }
    },

    // ==================== STAFF ====================

    async fetchStaff(params = {}) {
      this.loading.staff = true;
      this.error = null;
      try {
        const data = await getStaff(params);
        this.staff = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.staff = false;
      }
    },

    async fetchStaffMember(id) {
      this.loading.staff = true;
      try {
        const data = await getStaffMember(id);
        this.currentStaffMember = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.staff = false;
      }
    },

    async addStaffMember(data) {
      this.loading.staff = true;
      try {
        const result = await createStaffMember(data);
        this.staff.push(result);
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.staff = false;
      }
    },

    async modifyStaffMember(id, data) {
      this.loading.staff = true;
      try {
        const result = await updateStaffMember(id, data);
        const index = this.staff.findIndex((s) => s.id === id);
        if (index !== -1) this.staff[index] = result;
        return result;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.staff = false;
      }
    },

    async removeStaffMember(id) {
      this.loading.staff = true;
      try {
        await deleteStaffMember(id);
        this.staff = this.staff.filter((s) => s.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading.staff = false;
      }
    },

    // ==================== UTILITY ====================

    /**
     * Load all basic data at once.
     */
    async loadAllData() {
      await Promise.all([
        this.fetchWorkstations(),
        this.fetchProductionLines(),
        this.fetchCompanies(),
        this.fetchStaff(),
      ]);
    },
  },
});

export default useBasicDataStore;
