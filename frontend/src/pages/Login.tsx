import React from 'react'
import LoginForm from '../components/auth/LoginForm'

const Login: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-6">LMS Platform</h1>
        <h2 className="text-xl text-center mb-6 text-gray-600">Вход в систему</h2>
        <LoginForm />
      </div>
    </div>
  )
}

export default Login


