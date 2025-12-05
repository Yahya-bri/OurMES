/**
 * Maintenance Service
 *
 * API service for maintenance management.
 */
import httpClient from '@/core/api/httpClient';

const BASE_URL = '/mes/maintenance';

export const getMaintenanceLogs = async (params = {}) => {
  const response = await httpClient.get(`${BASE_URL}/logs/`, { params });
  return response.data;
};

export const getMaintenanceLog = async (id) => {
  const response = await httpClient.get(`${BASE_URL}/logs/${id}/`);
  return response.data;
};

export const createMaintenanceLog = async (data) => {
  const response = await httpClient.post(`${BASE_URL}/logs/`, data);
  return response.data;
};

export const updateMaintenanceLog = async (id, data) => {
  const response = await httpClient.patch(`${BASE_URL}/logs/${id}/`, data);
  return response.data;
};

export const deleteMaintenanceLog = async (id) => {
  await httpClient.delete(`${BASE_URL}/logs/${id}/`);
};

export const startMaintenance = async (workstationId, type, description, technicianName) => {
  const response = await httpClient.post(`${BASE_URL}/logs/start/`, {
    workstation_id: workstationId,
    type,
    description,
    technician_name: technicianName,
  });
  return response.data;
};

export const completeMaintenance = async (id, additionalNotes = '') => {
  const response = await httpClient.post(`${BASE_URL}/logs/${id}/complete/`, {
    additional_notes: additionalNotes,
  });
  return response.data;
};

export const getWorkstationDowntime = async (workstationId, days = 30) => {
  const response = await httpClient.get(`${BASE_URL}/logs/workstation-downtime/`, {
    params: { workstation_id: workstationId, days },
  });
  return response.data;
};

export const getTechnicianWorkload = async (technicianName, days = 30) => {
  const response = await httpClient.get(`${BASE_URL}/logs/technician-workload/`, {
    params: { technician_name: technicianName, days },
  });
  return response.data;
};

export const getMaintenanceStats = async () => {
  const response = await httpClient.get(`${BASE_URL}/logs/stats/`);
  return response.data;
};

export const getBreakdownFrequency = async (workstationId = null, days = 90) => {
  const params = { days };
  if (workstationId) params.workstation_id = workstationId;
  const response = await httpClient.get(`${BASE_URL}/logs/breakdown-frequency/`, { params });
  return response.data;
};

export const getActiveMaintenance = async () => {
  const response = await httpClient.get(`${BASE_URL}/logs/`, {
    params: { end_time__isnull: true },
  });
  return response.data;
};
