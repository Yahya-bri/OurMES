/**
 * Quality Service
 *
 * API service for quality management including inspections, quality checks,
 * NCRs, and SPC data.
 */
import httpClient from '@/core/api/httpClient';

const BASE_URL = '/mes/quality';

// ==================== INSPECTION CONFIG ====================

export const getInspectionConfigs = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/inspection-configs/`, { params });
  return response.data;
};

export const getInspectionConfig = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/inspection-configs/${id}/`);
  return response.data;
};

export const createInspectionConfig = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/inspection-configs/`, data);
  return response.data;
};

export const updateInspectionConfig = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/inspection-configs/${id}/`, data);
  return response.data;
};

export const deleteInspectionConfig = async (id) => {
  await httpClient.delete(`${BASE_URL}/inspection-configs/${id}/`);
};

// ==================== QUALITY CHECKS ====================

export const getQualityChecks = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/quality-checks/`, { params });
  return response.data;
};

export const getQualityCheck = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/quality-checks/${id}/`);
  return response.data;
};

export const createQualityCheck = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/quality-checks/`, data);
  return response.data;
};

export const recordQualityCheck = async (configId, orderNumber, resultValue, inspectorName) => {
  const response = await httpClient.post(`${BASE_URL}/quality-checks/record/`, {
    config_id: configId,
    order_number: orderNumber,
    result_value: resultValue,
    inspector_name: inspectorName,
  });
  return response.data;
};

export const getPassRate = async (configId = null, days = 30) => {
  const params = { days };
  if (configId) params.config_id = configId;
  const response = await httpClient.get(`${BASE_URL}/quality-checks/pass-rate/`, { params });
  return response.data;
};

// ==================== NCR ====================

export const getNCRs = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/ncrs/`, { params });
  return response.data;
};

export const getNCR = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/ncrs/${id}/`);
  return response.data;
};

export const createNCR = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/ncrs/`, data);
  return response.data;
};

export const updateNCR = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/ncrs/${id}/`, data);
  return response.data;
};

export const deleteNCR = async (id) => {
  await httpClient.delete(`${BASE_URL}/ncrs/${id}/`);
};

export const changeNCRStatus = async (id, newStatus) => {
  const response = await httpClient.post(`${BASE_URL}/ncrs/${id}/change_status/`, {
    status: newStatus,
  });
  return response.data;
};

export const setNCRDisposition = async (id, disposition) => {
  const response = await httpClient.post(`${BASE_URL}/ncrs/${id}/set_disposition/`, {
    disposition,
  });
  return response.data;
};

export const closeNCR = async (id, disposition = null) => {
  const response = await httpClient.post(`${BASE_URL}/ncrs/${id}/close/`, {
    disposition,
  });
  return response.data;
};

export const getNCRStats = async () => {
  const response = await httpClient.get(`${BASE_URL}/ncrs/stats/`);
  return response.data;
};

// ==================== SPC ====================

export const getSPCData = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/spc-data/`, { params });
  return response.data;
};

export const createSPCData = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/spc-data/`, data);
  return response.data;
};

export const recordSPCMeasurement = async (parameterName, value, machineId = '') => {
  const response = await httpClient.post(`${BASE_URL}/spc-data/record/`, {
    parameter_name: parameterName,
    value,
    machine_id: machineId,
  });
  return response.data;
};

export const getSPCStats = async (parameterName, limit = 100) => {
  const response = await httpClient.get(`${BASE_URL}/spc-data/stats/`, {
    params: { parameter_name: parameterName, limit },
  });
  return response.data;
};

export const getSPCControlChart = async (parameterName, limit = 50) => {
  const response = await httpClient.get(`${BASE_URL}/spc-data/control-chart/`, {
    params: { parameter_name: parameterName, limit },
  });
  return response.data;
};

export const checkSPCControl = async (parameterName, value) => {
  const response = await httpClient.post(`${BASE_URL}/spc-data/check-control/`, {
    parameter_name: parameterName,
    value,
  });
  return response.data;
};
