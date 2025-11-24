import React, { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, getCurrentUser } from '../api/auth'

interface User {
  id: string
  username: string
  email: string
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      loadUser()
    } else {
      setLoading(false)
    }
  }, [])

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser()
      setUser(userData)
    } catch (error) {
      localStorage.removeItem('access_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await apiLogin({ username, password })
    localStorage.setItem('access_token', response.access_token)
    await loadUser()
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}


