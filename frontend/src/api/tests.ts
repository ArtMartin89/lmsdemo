import api from './axios'

export interface AnswerSubmission {
  question_id: string
  answer: any
}

export interface TestSubmission {
  answers: AnswerSubmission[]
}

export interface TestResult {
  status: string
  result_id: string
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
  attempt_number: number
  next_module_unlocked?: string
}

export const getTestQuestions = async (moduleId: string) => {
  const response = await api.get(`/modules/${moduleId}/test`)
  return response.data
}

export const submitTest = async (moduleId: string, submission: TestSubmission): Promise<TestResult> => {
  const response = await api.post<TestResult>(`/modules/${moduleId}/test`, submission)
  return response.data
}

export const getTestResult = async (resultId: string) => {
  const response = await api.get(`/tests/results/${resultId}`)
  return response.data
}


