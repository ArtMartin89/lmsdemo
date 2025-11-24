import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitTest } from '../../api/tests'
import SingleChoice from './QuestionTypes/SingleChoice'
import MultipleChoice from './QuestionTypes/MultipleChoice'
import TextInput from './QuestionTypes/TextInput'
import Button from '../common/Button'

interface Question {
  question_id: string
  type: string
  question: string
  options?: Array<{ id: string; text: string }>
  points: number
  placeholder?: string
}

interface TestQuestionsProps {
  questions: Question[]
  moduleId: string
}

const TestQuestions: React.FC<TestQuestionsProps> = ({ questions, moduleId }) => {
  const navigate = useNavigate()
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [submitting, setSubmitting] = useState(false)

  const handleAnswerChange = (questionId: string, answer: any) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }))
  }

  const handleSubmit = async () => {
    try {
      setSubmitting(true)
      const formattedAnswers = Object.entries(answers).map(([question_id, answer]) => ({
        question_id,
        answer
      }))

      const result = await submitTest(moduleId, {
        answers: formattedAnswers
      })

      navigate(`/modules/${moduleId}/result`, {
        state: { result } as any
      })
    } catch (error: any) {
      console.error('Failed to submit test:', error)
      alert(error.response?.data?.detail || 'Ошибка отправки теста')
    } finally {
      setSubmitting(false)
    }
  }

  const renderQuestion = (question: Question) => {
    switch (question.type) {
      case 'single_choice':
        return (
          <SingleChoice
            question={question}
            value={answers[question.question_id]}
            onChange={(value) => handleAnswerChange(question.question_id, value)}
          />
        )
      case 'multiple_choice':
        return (
          <MultipleChoice
            question={question}
            value={answers[question.question_id] || []}
            onChange={(value) => handleAnswerChange(question.question_id, value)}
          />
        )
      case 'text_input':
        return (
          <TextInput
            question={question}
            value={answers[question.question_id] || ''}
            onChange={(value) => handleAnswerChange(question.question_id, value)}
          />
        )
      default:
        return null
    }
  }

  const allAnswered = questions.every(
    (q) => answers[q.question_id] !== undefined && answers[q.question_id] !== ''
  )

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6">Тест по модулю</h1>
        
        <div className="space-y-8">
          {questions.map((question, index) => (
            <div key={question.question_id} className="border-b pb-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold">
                  Вопрос {index + 1}
                </h3>
                <span className="text-sm text-gray-500">
                  {question.points} {question.points === 1 ? 'балл' : 'балла'}
                </span>
              </div>
              <p className="mb-4 text-gray-700">{question.question}</p>
              {renderQuestion(question)}
            </div>
          ))}
        </div>

        <div className="mt-8">
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!allAnswered || submitting}
            className="w-full"
          >
            {submitting ? 'Отправка...' : 'Отправить тест'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default TestQuestions

