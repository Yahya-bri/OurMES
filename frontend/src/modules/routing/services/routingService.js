import api from '@/core/api/httpClient';

export const getRoutings = async (params = {}) => {
  const response = await api.get('/mes/routing/routings/', { params });
  return response.data;
};

export const getRouting = async (id) => {
  const response = await api.get(`/mes/routing/routings/${id}/`);
  return response.data;
};

export const createRouting = async (data) => {
  const response = await api.post('/mes/routing/routings/', data);
  return response.data;
};

export const updateRouting = async (id, data) => {
  const response = await api.patch(`/mes/routing/routings/${id}/`, data);
  return response.data;
};

export const deleteRouting = async (id) => {
  const response = await api.delete(`/mes/routing/routings/${id}/`);
  return response.data;
};

export const changeRoutingState = async (id, state) => {
  const response = await api.post(`/mes/routing/routings/${id}/change_state/`, { state });
  return response.data;
};

export const getRoutingStats = async () => {
  const response = await api.get('/mes/routing/routings/stats/');
  return response.data;
};

export const getRoutingTree = async (id) => {
  const response = await api.get(`/mes/routing/routings/${id}/tree/`);
  return response.data;
};

export const bulkChangeRoutingState = async (ids, state) => {
  const response = await api.post('/mes/routing/routings/bulk_change_state/', { ids, state });
  return response.data;
};

export const bulkActivateRouting = async (ids) => {
  const response = await api.post('/mes/routing/routings/bulk_activate/', { ids });
  return response.data;
};

export const bulkDeactivateRouting = async (ids) => {
  const response = await api.post('/mes/routing/routings/bulk_deactivate/', { ids });
  return response.data;
};

export const bulkDeleteRouting = async (ids) => {
  const response = await api.post('/mes/routing/routings/bulk_delete/', { ids });
  return response.data;
};

export const setMasterRouting = async (id) => {
  const response = await api.post(`/mes/routing/routings/${id}/set_master/`);
  return response.data;
};

export const getOperations = async (params = {}) => {
  const response = await api.get('/mes/routing/operations/', { params });
  return response.data;
};

export const createOperation = async (data) => {
  const response = await api.post('/mes/routing/operations/', data);
  return response.data;
};

export const updateOperation = async (id, data) => {
  const response = await api.patch(`/mes/routing/operations/${id}/`, data);
  return response.data;
};

export const deleteOperation = async (id) => {
  const response = await api.delete(`/mes/routing/operations/${id}/`);
  return response.data;
};

// Routing Operation Components
export const getRoutingOperationComponents = async (technologyId) => {
  const response = await api.get('/mes/routing/routing-operations/', {
    params: { technology: technologyId }
  });
  return response.data;
};

export const createRoutingOperationComponent = async (data) => {
  const response = await api.post('/mes/routing/routing-operations/', data);
  return response.data;
};

export const updateRoutingOperationComponent = async (id, data) => {
  const response = await api.patch(`/mes/routing/routing-operations/${id}/`, data);
  return response.data;
};

export const deleteRoutingOperationComponent = async (id) => {
  const response = await api.delete(`/mes/routing/routing-operations/${id}/`);
  return response.data;
};

// Operation Product Components
export const createOperationProductIn = async (data) => {
  const response = await api.post('/mes/routing/operation-inputs/', data);
  return response.data;
};

export const updateOperationProductIn = async (id, data) => {
  const response = await api.patch(`/mes/routing/operation-inputs/${id}/`, data);
  return response.data;
};

export const deleteOperationProductIn = async (id) => {
  const response = await api.delete(`/mes/routing/operation-inputs/${id}/`);
  return response.data;
};

export const createOperationProductOut = async (data) => {
  const response = await api.post('/mes/routing/operation-outputs/', data);
  return response.data;
};

export const updateOperationProductOut = async (id, data) => {
  const response = await api.patch(`/mes/routing/operation-outputs/${id}/`, data);
  return response.data;
};

export const deleteOperationProductOut = async (id) => {
  const response = await api.delete(`/mes/routing/operation-outputs/${id}/`);
  return response.data;
};
