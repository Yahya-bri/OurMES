import api from '@/core/api/httpClient';

export const getScheduling = async (params = {}) => {
  const response = await api.get('/mes/scheduling/scheduling/', { params });
  return response.data;
};

export const getSchedulingByOrders = async (orderIds = []) => {
  const response = await api.get('/mes/scheduling/scheduling/by_orders/', { 
    params: { orders: orderIds.join(',') } 
  });
  return response.data;
};

export const generateSchedule = async (orderId, start = null) => {
  const response = await api.post(`/mes/scheduling/scheduling/generate/`, { order: orderId, start: start });
  return response.data;
};

export const generateMultiOrderSchedule = async (orderIds, start = null) => {
  const response = await api.post(`/mes/scheduling/scheduling/generate_multi/`, { 
    orders: orderIds, 
    start: start 
  });
  return response.data;
};

export const updateScheduleItem = async (id, data) => {
  const response = await api.patch(`/mes/scheduling/scheduling/${id}/`, data);
  return response.data;
};

export const bulkUpdateSchedule = async (updates) => {
  const response = await api.post(`/mes/scheduling/scheduling/bulk_update/`, { updates });
  return response.data;
};

export const deleteScheduleItem = async (id) => {
  const response = await api.delete(`/mes/scheduling/scheduling/${id}/`);
  return response.data;
};

export const deleteScheduleByOrder = async (orderId) => {
  const response = await api.delete(`/mes/scheduling/scheduling/by_order/${orderId}/`);
  return response.data;
};

export const checkConflicts = async (scheduleItems) => {
  const response = await api.post(`/mes/scheduling/scheduling/check_conflicts/`, { items: scheduleItems });
  return response.data;
};

export const optimizeSchedule = async (orderIds, method = 'earliest') => {
  const response = await api.post(`/mes/scheduling/scheduling/optimize/`, { 
    orders: orderIds, 
    method: method 
  });
  return response.data;
};
