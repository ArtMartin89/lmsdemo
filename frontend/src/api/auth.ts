import api from './axios'

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export const login = async (credentials: LoginCredentials): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/login', credentials)
  return response.data
}

export const register = async (data: RegisterData) => {
  const response = await api.post('/auth/register', data)
  return response.data
}

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me')
  return response.data
}


