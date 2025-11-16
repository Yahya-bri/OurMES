import api from '@/core/api/httpClient';

export const getOrders = async (params = {}) => {
  const response = await api.get('/mes/orders/orders/', { params });
  return response.data;
};

export const getOrder = async (id) => {
  const response = await api.get(`/mes/orders/orders/${id}/`);
  return response.data;
};

export const createOrder = async (data) => {
  const response = await api.post('/mes/orders/orders/', data);
  return response.data;
};

export const updateOrder = async (id, data) => {
  const response = await api.patch(`/mes/orders/orders/${id}/`, data);
  return response.data;
};

export const deleteOrder = async (id) => {
  const response = await api.delete(`/mes/orders/orders/${id}/`);
  return response.data;
};

export const changeOrderState = async (id, data) => {
  const response = await api.post(`/mes/orders/orders/${id}/change_state/`, data);
  return response.data;
};

export const getOrderStats = async () => {
  const response = await api.get('/mes/orders/orders/dashboard_stats/');
  return response.data;
};
