import { defineStore } from 'pinia';
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from '../services/productsService';

export const useProductsStore = defineStore('products', {
  state: () => ({
    products: [],
    currentProduct: null,
    loading: false,
    error: null,
  }),
  
  actions: {
    async fetchProducts(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getProducts(params);
        this.products = data.results || data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async fetchProduct(id) {
      this.loading = true;
      this.error = null;
      try {
        const data = await getProduct(id);
        this.currentProduct = data;
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async addProduct(productData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await createProduct(productData);
        this.products.unshift(data);
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async modifyProduct(id, productData) {
      this.loading = true;
      this.error = null;
      try {
        const data = await updateProduct(id, productData);
        const index = this.products.findIndex(p => p.id === id);
        if (index !== -1) {
          this.products[index] = data;
        }
        return data;
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async removeProduct(id) {
      this.loading = true;
      this.error = null;
      try {
        await deleteProduct(id);
        this.products = this.products.filter(p => p.id !== id);
      } catch (error) {
        this.error = error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },
  },
});
