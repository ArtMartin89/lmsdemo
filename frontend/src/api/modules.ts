import api from './axios'

export interface Module {
  id: string
  title: string
  description: string
  total_lessons: number
  order_index: number
  is_active: boolean
}

export interface LessonResponse {
  status: string
  lesson_number?: number
  total_lessons?: number
  content?: string
  content_type?: string
  module_id?: string
  progress_percentage?: number
  message?: string
  test_available?: boolean
  test_questions?: any
  test_result_id?: string
}

export const getModules = async (): Promise<Module[]> => {
  const response = await api.get<Module[]>('/modules')
  return response.data
}

export const getModule = async (moduleId: string): Promise<Module> => {
  const response = await api.get<Module>(`/modules/${moduleId}`)
  return response.data
}

export const startModule = async (moduleId: string) => {
  const response = await api.post(`/modules/${moduleId}/start`)
  return response.data
}

export const getNextLesson = async (moduleId: string): Promise<LessonResponse> => {
  const response = await api.post<LessonResponse>(`/modules/${moduleId}/next`)
  return response.data
}


