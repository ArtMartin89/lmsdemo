import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { getNextLesson } from '../../api/modules'
import ProgressBar from '../common/ProgressBar'
import Button from '../common/Button'
import Loading from '../common/Loading'

interface LessonData {
  lesson_number: number
  total_lessons: number
  content: string
  progress_percentage: number
  module_id: string
}

const LessonViewer: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>()
  const navigate = useNavigate()
  const [lesson, setLesson] = useState<LessonData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadLesson()
  }, [moduleId])

  const loadLesson = async () => {
    try {
      setLoading(true)
      const response = await getNextLesson(moduleId!)
      
      if (response.status === 'module_completed') {
        navigate(`/modules/${moduleId}/test`, {
          state: { testQuestions: response.test_questions } as any
        })
      } else if (response.status === 'success') {
        setLesson({
          lesson_number: response.lesson_number!,
          total_lessons: response.total_lessons!,
          content: response.content!,
          progress_percentage: response.progress_percentage!,
          module_id: response.module_id!
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки урока')
    } finally {
      setLoading(false)
    }
  }

  const handleNext = async () => {
    try {
      setLoading(true)
      const response = await getNextLesson(moduleId!)
      
      if (response.status === 'module_completed') {
        navigate(`/modules/${moduleId}/test`, {
          state: { testQuestions: response.test_questions } as any
        })
      } else if (response.status === 'success') {
        setLesson({
          lesson_number: response.lesson_number!,
          total_lessons: response.total_lessons!,
          content: response.content!,
          progress_percentage: response.progress_percentage!,
          module_id: response.module_id!
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки урока')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !lesson) return <Loading />
  if (error) return <div className="text-red-600 p-4">Ошибка: {error}</div>
  if (!lesson) return null

  return (
    <div className="max-w-4xl mx-auto p-6">
      <ProgressBar 
        current={lesson.lesson_number} 
        total={lesson.total_lessons}
        percentage={lesson.progress_percentage}
      />
      
      <div className="bg-white rounded-lg shadow-lg p-8 mt-6">
        <h1 className="text-3xl font-bold mb-4">
          Урок {lesson.lesson_number} из {lesson.total_lessons}
        </h1>
        
        <div className="prose max-w-none">
          <ReactMarkdown>{lesson.content}</ReactMarkdown>
        </div>
        
        <div className="mt-8 flex justify-between">
          <Button 
            variant="secondary"
            onClick={() => navigate(`/dashboard`)}
          >
            Вернуться к модулю
          </Button>
          
          <Button 
            variant="primary"
            onClick={handleNext}
            disabled={loading}
          >
            {loading ? 'Загрузка...' : 'Дальше'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default LessonViewer

