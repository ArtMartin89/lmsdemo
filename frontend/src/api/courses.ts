import api from './axios'

export interface Course {
  id: string
  title: string
  description?: string
  order_index: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Module {
  id: string
  title: string
  description?: string
  total_lessons: number
  order_index: number
  is_active: boolean
  course_id: string
}

export interface CourseWithModules extends Course {
  modules: Module[]
}

export const getCourses = async (): Promise<CourseWithModules[]> => {
  const response = await api.get<CourseWithModules[]>('/courses')
  return response.data
}

export const getCourse = async (courseId: string): Promise<CourseWithModules> => {
  const response = await api.get<CourseWithModules>(`/courses/${courseId}`)
  return response.data
}

