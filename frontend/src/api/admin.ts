import axios from './axios';

export interface ModuleCreate {
  id: string;
  title: string;
  description?: string;
  total_lessons: number;
  order_index: number;
  is_active?: boolean;
}

export interface ModuleUpdate {
  title?: string;
  description?: string;
  total_lessons?: number;
  order_index?: number;
  is_active?: boolean;
}

export interface LessonContent {
  module_id: string;
  lesson_number: number;
  content: string;
  content_type: string;
  files?: string[];
}

// Module Management
export const adminApi = {
  // Modules
  listModules: async () => {
    const response = await axios.get('/api/v1/admin/modules');
    return response.data;
  },

  createModule: async (moduleData: ModuleCreate) => {
    const response = await axios.post('/api/v1/admin/modules', moduleData);
    return response.data;
  },

  getModule: async (moduleId: string) => {
    const response = await axios.get(`/api/v1/admin/modules/${moduleId}`);
    return response.data;
  },

  updateModule: async (moduleId: string, moduleData: ModuleUpdate) => {
    const response = await axios.put(`/api/v1/admin/modules/${moduleId}`, moduleData);
    return response.data;
  },

  deleteModule: async (moduleId: string) => {
    await axios.delete(`/api/v1/admin/modules/${moduleId}`);
  },

  // Lessons
  getLesson: async (moduleId: string, lessonNumber: number): Promise<LessonContent> => {
    const response = await axios.get(`/api/v1/admin/modules/${moduleId}/lessons/${lessonNumber}`);
    return response.data;
  },

  saveLesson: async (moduleId: string, lessonNumber: number, content: string) => {
    const formData = new FormData();
    formData.append('content', content);
    const response = await axios.post(
      `/api/v1/admin/modules/${moduleId}/lessons/${lessonNumber}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Files
  uploadFile: async (
    moduleId: string,
    lessonNumber: number,
    file: File
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(
      `/api/v1/admin/modules/${moduleId}/lessons/${lessonNumber}/files`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  getFileUrl: (moduleId: string, lessonNumber: number, filename: string) => {
    return `/api/v1/admin/files/${moduleId}/${lessonNumber}/${filename}`;
  },

  deleteFile: async (moduleId: string, lessonNumber: number, filename: string) => {
    await axios.delete(`/api/v1/admin/files/${moduleId}/${lessonNumber}/${filename}`);
  },
};

