import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { getCourses, CourseWithModules } from '../api/courses'
import { getProgress } from '../api/progress'
import ModuleCard from '../components/dashboard/ModuleCard'
import Button from '../components/common/Button'
import Loading from '../components/common/Loading'

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth()
  const [courses, setCourses] = useState<CourseWithModules[]>([])
  const [progress, setProgress] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [user])

  const loadData = async () => {
    try {
      const [coursesData, progressData] = await Promise.all([
        getCourses(),
        getProgress()
      ])
      console.log('Loaded courses:', coursesData)
      console.log('Loaded progress:', progressData)
      setCourses(coursesData)
      setProgress(progressData)
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Ошибка загрузки данных. Проверьте консоль браузера.')
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
            {user?.is_superuser === true && (
              <Link to="/admin/courses">
                <Button variant="secondary">Админ-панель</Button>
              </Link>
            )}
            <span className="text-gray-700">
              Привет, {user?.username}!
            </span>
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

        {courses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-gray-500 text-lg">Курсы не найдены</p>
            <p className="text-gray-400 mt-2">Обратитесь к администратору для добавления курсов</p>
          </div>
        ) : (
          <div className="space-y-8">
            {courses.map((course) => (
              <div key={course.id} className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-2">{course.title}</h2>
                {course.description && (
                  <p className="text-gray-600 mb-4">{course.description}</p>
                )}
                {course.modules.length === 0 ? (
                  <p className="text-gray-500">В этом курсе пока нет модулей</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {course.modules.map((module) => {
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
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard

