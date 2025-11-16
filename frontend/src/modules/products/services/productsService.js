import api from '@/core/api/httpClient';

export const getProducts = async (params = {}) => {
  const response = await api.get('/mes/basic/products/', { params });
  return response.data;
};

export const getProduct = async (id) => {
  const response = await api.get(`/mes/basic/products/${id}/`);
  return response.data;
};

export const createProduct = async (data) => {
  const response = await api.post('/mes/basic/products/', data);
  return response.data;
};

export const updateProduct = async (id, data) => {
  const response = await api.patch(`/mes/basic/products/${id}/`, data);
  return response.data;
};

export const deleteProduct = async (id) => {
  const response = await api.delete(`/mes/basic/products/${id}/`);
  return response.data;
};
