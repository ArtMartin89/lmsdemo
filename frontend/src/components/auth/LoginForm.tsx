import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import Button from '../common/Button'

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Login error:', err)
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка входа. Проверьте данные.'
      setError(errorMessage)
      
      // Если ошибка сети, показываем более информативное сообщение
      if (!err.response) {
        setError('Не удалось подключиться к серверу. Проверьте, что API запущен на http://localhost:8000')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
          Имя пользователя
        </label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="testdemo"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
          Пароль
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="demotest"
        />
      </div>

      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Вход...' : 'Войти'}
      </Button>
    </form>
  )
}

export default LoginForm

