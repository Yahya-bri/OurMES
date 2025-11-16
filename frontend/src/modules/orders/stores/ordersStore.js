import { defineStore } from 'pinia';
import { getOrders, getOrder, createOrder, updateOrder, deleteOrder, changeOrderState, getOrderStats } from '../services/ordersService';

export const useOrdersStore = defineStore('orders', {
  state: () => ({
    orders: [],
    currentOrder: null,
    stats: {
      total: 0,
      pending: 0,
      in_progress: 0,
      completed: 0,
    },
    loading: false,
    error: null,
  }),
  
  actions: {
    async fetchOrders(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getOrders(params);
        this.orders = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchOrder(id) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getOrder(id);
        this.currentOrder = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async addOrder(orderData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await createOrder(orderData);
        this.orders.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async modifyOrder(id, orderData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await updateOrder(id, orderData);
        const index = this.orders.findIndex(o => o.id === id);
        if (index !== -1) {
          this.orders[index] = data;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async removeOrder(id) {
      this.loading = true;
      this.error = null;
      try {
        await deleteOrder(id);
        this.orders = this.orders.filter(o => o.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async updateOrderState(id, state, worker = '') {
      this.loading = true;
      this.error = null;
      try {
        const data = await changeOrderState(id, state, worker);
        const index = this.orders.findIndex(o => o.id === id);
        if (index !== -1) {
          this.orders[index].state = state;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchStats() {
      try {
        const data = await getOrderStats();
        this.stats = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      }
    },
  },
});
