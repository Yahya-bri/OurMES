import api from '@/core/api/httpClient';

export const getCompanies = async (params = {}) => {
  const response = await api.get('/mes/basic/companies/', { params });
  return response.data;
};

export const getCompany = async (id) => {
  const response = await api.get(`/mes/basic/companies/${id}/`);
  return response.data;
};

export const createCompany = async (data) => {
  const response = await api.post('/mes/basic/companies/', data);
  return response.data;
};

export const updateCompany = async (id, data) => {
  const response = await api.patch(`/mes/basic/companies/${id}/`, data);
  return response.data;
};

export const deleteCompany = async (id) => {
  const response = await api.delete(`/mes/basic/companies/${id}/`);
  return response.data;
};

export const getWorkstations = async (params = {}) => {
  const response = await api.get('/mes/basic/workstations/', { params });
  return response.data;
};

export const createWorkstation = async (data) => {
  const response = await api.post('/mes/basic/workstations/', data);
  return response.data;
};

export const updateWorkstation = async (id, data) => {
  const response = await api.patch(`/mes/basic/workstations/${id}/`, data);
  return response.data;
};

export const deleteWorkstation = async (id) => {
  const response = await api.delete(`/mes/basic/workstations/${id}/`);
  return response.data;
};

export const getProductionLines = async (params = {}) => {
  const response = await api.get('/mes/basic/production-lines/', { params });
  return response.data;
};

export const createProductionLine = async (data) => {
  const response = await api.post('/mes/basic/production-lines/', data);
  return response.data;
};

export const getStaff = async (params = {}) => {
  const response = await api.get('/mes/basic/staff/', { params });
  return response.data;
};

export const createStaff = async (data) => {
  const response = await api.post('/mes/basic/staff/', data);
  return response.data;
};

export const updateStaff = async (id, data) => {
  const response = await api.patch(`/mes/basic/staff/${id}/`, data);
  return response.data;
};

export const deleteStaff = async (id) => {
  const response = await api.delete(`/mes/basic/staff/${id}/`);
  return response.data;
};

export const updateProductionLine = async (id, data) => {
  const response = await api.patch(`/mes/basic/production-lines/${id}/`, data);
  return response.data;
};

export const deleteProductionLine = async (id) => {
  const response = await api.delete(`/mes/basic/production-lines/${id}/`);
  return response.data;
};

export const getOperations = async (params = {}) => {
  const response = await api.get('/mes/routing/operations/', { params });
  return response.data;
};
