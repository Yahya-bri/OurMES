/**
 * Inventory Service
 *
 * API service for inventory management including stock, containers,
 * traceability, and kanban.
 */
import httpClient from '@/core/api/httpClient';

const BASE_URL = '/mes/inventory';

// ==================== STOCK ====================

export const getStocks = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/stocks/`, { params });
  return response.data;
};

export const getStock = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/stocks/${id}/`);
  return response.data;
};

export const createStock = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/stocks/`, data);
  return response.data;
};

export const updateStock = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/stocks/${id}/`, data);
  return response.data;
};

export const deleteStock = async (id) => {
  await httpClient.delete(`${BASE_URL}/stocks/${id}/`);
};

export const adjustStock = async (id, quantityChange, reason = '') => {
  const response = await httpClient.post(`${BASE_URL}/stocks/${id}/adjust/`, {
    quantity_change: quantityChange,
    reason,
  });
  return response.data;
};

export const transferStock = async (materialId, fromLocation, toLocation, quantity) => {
  const response = await httpClient.post(`${BASE_URL}/stocks/transfer/`, {
    material_id: materialId,
    from_location: fromLocation,
    to_location: toLocation,
    quantity,
  });
  return response.data;
};

// ==================== CONTAINERS ====================

export const getContainers = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/containers/`, { params });
  return response.data;
};

export const getContainer = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/containers/${id}/`);
  return response.data;
};

export const createContainer = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/containers/`, data);
  return response.data;
};

export const updateContainer = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/containers/${id}/`, data);
  return response.data;
};

export const deleteContainer = async (id) => {
  await httpClient.delete(`${BASE_URL}/containers/${id}/`);
};

export const fillContainer = async (containerId, materialId, quantity) => {
  const response = await httpClient.post(`${BASE_URL}/containers/${containerId}/fill/`, {
    material_id: materialId,
    quantity,
  });
  return response.data;
};

export const emptyContainer = async (containerId) => {
  const response = await httpClient.post(`${BASE_URL}/containers/${containerId}/empty/`);
  return response.data;
};

export const moveContainer = async (containerId, newLocation) => {
  const response = await httpClient.post(`${BASE_URL}/containers/${containerId}/move/`, {
    location: newLocation,
  });
  return response.data;
};

// ==================== TRACEABILITY ====================

export const getTraceabilityRecords = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/traceability/`, { params });
  return response.data;
};

export const createTraceabilityRecord = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/traceability/`, data);
  return response.data;
};

export const traceForward = async (rawMaterialBatch) => {
  const response = await httpClient.get(`${BASE_URL}/traceability/forward/`, {
    params: { batch: rawMaterialBatch },
  });
  return response.data;
};

export const traceBackward = async (finishedGoodBatch) => {
  const response = await httpClient.get(`${BASE_URL}/traceability/backward/`, {
    params: { batch: finishedGoodBatch },
  });
  return response.data;
};

export const getGenealogy = async (finishedGoodBatch) => {
  const response = await httpClient.get(`${BASE_URL}/traceability/genealogy/`, {
    params: { batch: finishedGoodBatch },
  });
  return response.data;
};

// ==================== KANBAN ====================

export const getKanbanCards = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/kanban/`, { params });
  return response.data;
};

export const getKanbanCard = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/kanban/${id}/`);
  return response.data;
};

export const createKanbanCard = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/kanban/`, data);
  return response.data;
};

export const updateKanbanCard = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/kanban/${id}/`, data);
  return response.data;
};

export const deleteKanbanCard = async (id) => {
  await httpClient.delete(`${BASE_URL}/kanban/${id}/`);
};

export const triggerReplenishment = async (id) => {
  const response = await httpClient.post(`${BASE_URL}/kanban/${id}/trigger_replenishment/`);
  return response.data;
};

export const completeReplenishment = async (id) => {
  const response = await httpClient.post(`${BASE_URL}/kanban/${id}/complete_replenishment/`);
  return response.data;
};

export const markKanbanEmpty = async (id, autoTrigger = true) => {
  const response = await httpClient.post(`${BASE_URL}/kanban/${id}/mark_empty/`, {
    auto_trigger: autoTrigger,
  });
  return response.data;
};

export const getKanbanStats = async () => {
  const response = await httpClient.get(`${BASE_URL}/kanban/stats/`);
  return response.data;
};
