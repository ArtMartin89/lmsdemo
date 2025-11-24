import api from './axios'

export interface Progress {
  module_id: string
  current_lesson: number
  total_lessons: number
  status: string
  progress_percentage: number
  started_at: string
  updated_at: string
  completed_at?: string
}

export interface OverallProgress {
  total_modules: number
  completed_modules: number
  in_progress_modules: number
  average_grade?: number
  modules: Progress[]
}

export const getProgress = async (): Promise<OverallProgress> => {
  const response = await api.get<OverallProgress>('/progress')
  return response.data
}

export const getModuleProgress = async (moduleId: string): Promise<Progress> => {
  const response = await api.get<Progress>(`/progress/${moduleId}`)
  return response.data
}


