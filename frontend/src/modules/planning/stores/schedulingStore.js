/**
 * Scheduling Store
 *
 * Centralized state management for production scheduling.
 * Handles schedule items, conflicts, and scheduling operations.
 */
import { defineStore } from 'pinia';
import {
  getScheduleItems,
  getScheduleItem,
  createScheduleItem,
  updateScheduleItem,
  deleteScheduleItem,
  generateSchedule,
  detectConflicts,
  lockScheduleItem,
  unlockScheduleItem,
  shiftSchedule,
  getScheduleStats,
} from '../services/schedulingService';

export const useSchedulingStore = defineStore('scheduling', {
  state: () => ({
    // Data
    scheduleItems: [],
    currentItem: null,
    conflicts: [],
    stats: {
      total: 0,
      locked: 0,
      today: 0,
      this_week: 0,
    },
    // UI State
    loading: false,
    generating: false,
    error: null,
    // Filters
    filters: {
      order: null,
      productionLine: null,
      dateRange: null,
      status: null,
    },
  }),

  getters: {
    /**
     * Get schedule items for a specific order.
     */
    itemsByOrder: (state) => (orderId) => {
      return state.scheduleItems.filter((item) => item.order === orderId);
    },

    /**
     * Get locked items count.
     */
    lockedCount: (state) => {
      return state.scheduleItems.filter((item) => item.locked).length;
    },

    /**
     * Check if there are conflicts.
     */
    hasConflicts: (state) => {
      return state.conflicts.length > 0;
    },

    /**
     * Get items filtered by current filters.
     */
    filteredItems: (state) => {
      let items = [...state.scheduleItems];

      if (state.filters.order) {
        items = items.filter((item) => item.order === state.filters.order);
      }

      if (state.filters.status === 'locked') {
        items = items.filter((item) => item.locked);
      } else if (state.filters.status === 'unlocked') {
        items = items.filter((item) => !item.locked);
      }

      return items;
    },
  },

  actions: {
    /**
     * Fetch schedule items from API.
     */
    async fetchScheduleItems(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getScheduleItems(params);
        this.scheduleItems = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch a single schedule item.
     */
    async fetchScheduleItem(id) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getScheduleItem(id);
        this.currentItem = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Create a new schedule item.
     */
    async addScheduleItem(itemData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await createScheduleItem(itemData);
        this.scheduleItems.push(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Update a schedule item.
     */
    async modifyScheduleItem(id, itemData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await updateScheduleItem(id, itemData);
        const index = this.scheduleItems.findIndex((item) => item.id === id);
        if (index !== -1) {
          this.scheduleItems[index] = data;
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
     * Delete a schedule item.
     */
    async removeScheduleItem(id) {
      this.loading = true;
      this.error = null;
      try {
        await deleteScheduleItem(id);
        this.scheduleItems = this.scheduleItems.filter((item) => item.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Generate schedule for an order.
     */
    async generateOrderSchedule(orderId, startTime) {
      this.generating = true;
      this.error = null;
      try {
        const data = await generateSchedule(orderId, startTime);
        // Add generated items to state
        if (Array.isArray(data)) {
          this.scheduleItems.push(...data);
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.generating = false;
      }
    },

    /**
     * Detect scheduling conflicts.
     */
    async checkConflicts(startDate, endDate) {
      this.loading = true;
      this.error = null;
      try {
        const data = await detectConflicts(startDate, endDate);
        this.conflicts = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Lock a schedule item.
     */
    async lockItem(id) {
      try {
        const data = await lockScheduleItem(id);
        const index = this.scheduleItems.findIndex((item) => item.id === id);
        if (index !== -1) {
          this.scheduleItems[index].locked = true;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    /**
     * Unlock a schedule item.
     */
    async unlockItem(id) {
      try {
        const data = await unlockScheduleItem(id);
        const index = this.scheduleItems.findIndex((item) => item.id === id);
        if (index !== -1) {
          this.scheduleItems[index].locked = false;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    /**
     * Shift all schedule items for an order.
     */
    async shiftOrderSchedule(orderId, deltaSeconds) {
      this.loading = true;
      this.error = null;
      try {
        await shiftSchedule(orderId, deltaSeconds);
        // Refresh to get updated times
        await this.fetchScheduleItems({ order: orderId });
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch statistics.
     */
    async fetchStats() {
      try {
        const data = await getScheduleStats();
        this.stats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },

    /**
     * Set filters.
     */
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },

    /**
     * Clear all filters.
     */
    clearFilters() {
      this.filters = {
        order: null,
        productionLine: null,
        dateRange: null,
        status: null,
      };
    },

    /**
     * Clear conflicts.
     */
    clearConflicts() {
      this.conflicts = [];
    },
  },
});

export default useSchedulingStore;
