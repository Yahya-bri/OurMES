import api from '@/core/api/httpClient';

export const getProductionCounting = async (params = {}) => {
  const response = await api.get('/mes/production-counting/production-counting/', { params });
  return response.data;
};

export const createProductionRecord = async (data) => {
  const response = await api.post('/mes/production-counting/production-counting/', data);
  return response.data;
};

export const updateProductionRecord = async (id, data) => {
  const response = await api.patch(`/mes/production-counting/production-counting/${id}/`, data);
  return response.data;
};

export const getOrderProgress = async (orderId) => {
  const response = await api.get(`/mes/production-counting/production-counting/order_progress/?order_id=${orderId}`);
  return response.data;
};

export const startOperation = async (data) => {
  // data: { order, operation, workstation, operator }
  return createProductionRecord({
    ...data,
    status: 'in_progress',
    produced_quantity: 0,
    scrap_quantity: 0,
    start_time: new Date().toISOString(),
  });
};

export const stopOperation = async (id, producedQty, scrapQty) => {
  const response = await api.post(`/mes/production-counting/production-counting/${id}/stop/`, {
    produced_quantity: producedQty,
    scrap_quantity: scrapQty,
  });
  return response.data;
};

export const reportQuantity = async (id, producedQty, scrapQty) => {
  const response = await api.post(`/mes/production-counting/production-counting/${id}/report/`, {
    produced_quantity: producedQty,
    scrap_quantity: scrapQty,
  });
  return response.data;
};
