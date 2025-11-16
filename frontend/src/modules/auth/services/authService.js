import api from '@/core/api/httpClient';

export async function login(username, password) {
  const res = await api.post('/security/token/', { username, password });
  return res.data; // { access, refresh }
}

export async function refreshToken(refresh) {
  const res = await api.post('/security/token/refresh/', { refresh });
  return res.data; // { access }
}

export async function getMe() {
  const res = await api.get('/security/me/');
  return res.data;
}
