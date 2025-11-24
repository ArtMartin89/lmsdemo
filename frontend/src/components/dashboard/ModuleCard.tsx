import React from 'react'
import { useNavigate } from 'react-router-dom'
import { startModule } from '../../api/modules'
import Button from '../common/Button'
import ProgressBar from '../common/ProgressBar'

interface ModuleCardProps {
  module: {
    id: string
    title: string
    description: string
    total_lessons: number
  }
  progress?: {
    current_lesson: number
    total_lessons: number
    status: string
    progress_percentage: number
    completed_at?: string
  }
  grade?: number
}

const ModuleCard: React.FC<ModuleCardProps> = ({ module, progress, grade }) => {
  const navigate = useNavigate()

  const handleStart = async () => {
    try {
      await startModule(module.id)
      navigate(`/modules/${module.id}/lesson`)
    } catch (error: any) {
      // If already started, just navigate
      if (error.response?.status === 400 || error.response?.status === 200) {
        navigate(`/modules/${module.id}/lesson`)
      } else {
        console.error('Error starting module:', error)
        navigate(`/modules/${module.id}/lesson`)
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
      case 'testing':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершен'
      case 'in_progress':
        return 'В процессе'
      case 'testing':
        return 'Тестирование'
      case 'failed':
        return 'Не пройден'
      default:
        return 'Не начат'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold mb-2">{module.title}</h3>
          <p className="text-gray-600 text-sm">{module.description}</p>
        </div>
        {grade !== undefined && (
          <div className="text-2xl font-bold text-blue-600">
            {grade}/10
          </div>
        )}
      </div>

      {progress && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(progress.status)}`}>
              {getStatusText(progress.status)}
            </span>
          </div>
          <ProgressBar
            current={progress.current_lesson}
            total={progress.total_lessons}
            percentage={progress.progress_percentage}
          />
        </div>
      )}

      <Button
        variant="primary"
        onClick={handleStart}
        className="w-full"
      >
        {progress ? 'Продолжить' : 'Начать модуль'}
      </Button>
    </div>
  )
}

export default ModuleCard

