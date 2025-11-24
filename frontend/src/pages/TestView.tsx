import React, { useEffect, useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { getTestQuestions } from '../api/tests'
import TestQuestions from '../components/test/TestQuestions'
import Loading from '../components/common/Loading'

interface LocationState {
  testQuestions?: any
}

const TestView: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const [questions, setQuestions] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadQuestions()
  }, [moduleId])

  const loadQuestions = async () => {
    try {
      // Check if questions were passed from lesson
      const state = location.state as LocationState | null
      if (state?.testQuestions) {
        setQuestions(state.testQuestions)
        setLoading(false)
        return
      }

      // Otherwise fetch from API
      const data = await getTestQuestions(moduleId!)
      setQuestions(data)
    } catch (error: any) {
      console.error('Failed to load test questions:', error)
      if (error.response?.status === 400) {
        navigate('/dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading />
  if (!questions || !questions.questions) return <div>Тест не найден</div>

  return <TestQuestions questions={questions.questions} moduleId={moduleId!} />
}

export default TestView

