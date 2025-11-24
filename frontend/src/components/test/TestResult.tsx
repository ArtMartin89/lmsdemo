import React from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../common/Button'

interface TestResultProps {
  result: {
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

const TestResult: React.FC<TestResultProps> = ({ result }) => {
  const navigate = useNavigate()
  const grade = Math.round((result.percentage / 100) * 10)

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">
            {result.passed ? 'Тест пройден!' : 'Тест не пройден'}
          </h1>
          <div className="text-6xl font-bold mb-2">
            {grade}/10
          </div>
          <p className="text-gray-600">
            {result.score} из {result.max_score} правильных ответов ({result.percentage}%)
          </p>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Детальные результаты:</h2>
          <div className="space-y-4">
            {result.detailed_results.map((detail, index) => (
              <div
                key={detail.question_id}
                className={`p-4 rounded-lg border-2 ${
                  detail.correct
                    ? 'border-green-200 bg-green-50'
                    : 'border-red-200 bg-red-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium mb-2">Вопрос {index + 1}</p>
                    <p className="text-sm text-gray-600">
                      Ваш ответ: <span className="font-medium">{String(detail.user_answer)}</span>
                    </p>
                    {!detail.correct && detail.correct_answer && (
                      <p className="text-sm text-green-600 mt-1">
                        Правильный ответ: <span className="font-medium">{String(detail.correct_answer)}</span>
                      </p>
                    )}
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      detail.correct
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {detail.correct ? '✓ Правильно' : '✗ Неправильно'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {result.next_module_unlocked && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">
              🎉 Модуль {result.next_module_unlocked} разблокирован!
            </p>
          </div>
        )}

        <div className="flex justify-center">
          <Button variant="primary" onClick={() => navigate('/dashboard')}>
            Вернуться к дашборду
          </Button>
        </div>
      </div>
    </div>
  )
}

export default TestResult


