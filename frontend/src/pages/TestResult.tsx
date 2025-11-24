import React from 'react'
import { useLocation } from 'react-router-dom'
import TestResultComponent from '../components/test/TestResult'

interface LocationState {
  result?: {
    score: number
    max_score: number
    percentage: number
    passed: boolean
    detailed_results: Array<{
      question_id: string
      correct: boolean
      user_answer: any
      correct_answer?: any
    }>
    next_module_unlocked?: string
  }
}

const TestResultPage: React.FC = () => {
  const location = useLocation()
  const state = location.state as LocationState | null
  const result = state?.result

  if (!result) {
    return <div className="p-4">Результаты не найдены</div>
  }

  return <TestResultComponent result={result} />
}

export default TestResultPage

