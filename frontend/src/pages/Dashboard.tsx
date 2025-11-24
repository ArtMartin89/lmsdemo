import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getModules } from '../api/modules'
import { getProgress } from '../api/progress'
import ModuleCard from '../components/dashboard/ModuleCard'
import Button from '../components/common/Button'
import Loading from '../components/common/Loading'

interface Module {
  id: string
  title: string
  description: string
  total_lessons: number
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth()
  const [modules, setModules] = useState<Module[]>([])
  const [progress, setProgress] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [modulesData, progressData] = await Promise.all([
        getModules(),
        getProgress()
      ])
      setModules(modulesData)
      setProgress(progressData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading />

  const progressMap = new Map(
    progress?.modules.map((p: any) => [p.module_id, p]) || []
  )

  const gradeMap = new Map()
  if (progress?.modules) {
    progress.modules.forEach((p: any) => {
      if (p.status === 'completed') {
        // Calculate grade from test results if available
        gradeMap.set(p.module_id, 8) // Placeholder - should fetch from test results
      }
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">LMS Platform</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Привет, {user?.username}!</span>
            <Button variant="secondary" onClick={logout}>
              Выйти
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {progress && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Общий прогресс</h2>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Всего модулей</p>
                <p className="text-2xl font-bold">{progress.total_modules}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Завершено</p>
                <p className="text-2xl font-bold text-green-600">{progress.completed_modules}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Средняя оценка</p>
                <p className="text-2xl font-bold text-blue-600">
                  {progress.average_grade ? `${progress.average_grade}/10` : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => {
            const moduleProgress = progressMap.get(module.id) as {
              current_lesson: number
              total_lessons: number
              status: string
              progress_percentage: number
              completed_at?: string
            } | undefined
            const grade = gradeMap.get(module.id)

            return (
              <ModuleCard
                key={module.id}
                module={module}
                progress={moduleProgress}
                grade={grade}
              />
            )
          })}
        </div>
      </main>
    </div>
  )
}

export default Dashboard

