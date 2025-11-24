import axios from './axios';

export interface CourseCreate {
  title: string;
  description?: string;
  order_index: number;
  is_active?: boolean;
}

export interface CourseUpdate {
  title?: string;
  description?: string;
  order_index?: number;
  is_active?: boolean;
}

export interface Course {
  id: string;
  title: string;
  description?: string;
  order_index: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CourseWithModules extends Course {
  modules: Module[];
}

export interface Module {
  id: string;
  title: string;
  description?: string;
  total_lessons: number;
  order_index: number;
  is_active: boolean;
}

export interface ModuleCreate {
  id: string;
  course_id: string;
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

// Course and Module Management
export const adminApi = {
  // Courses
  listCourses: async (): Promise<Course[]> => {
    const response = await axios.get('/admin/courses');
    return response.data;
  },

  getCourse: async (courseId: string): Promise<CourseWithModules> => {
    const response = await axios.get(`/admin/courses/${courseId}`);
    return response.data;
  },

  createCourse: async (courseData: CourseCreate): Promise<Course> => {
    const response = await axios.post('/admin/courses', courseData);
    return response.data;
  },

  updateCourse: async (courseId: string, courseData: CourseUpdate): Promise<Course> => {
    const response = await axios.put(`/admin/courses/${courseId}`, courseData);
    return response.data;
  },

  deleteCourse: async (courseId: string): Promise<void> => {
    await axios.delete(`/admin/courses/${courseId}`);
  },

  // Modules
  listModules: async (courseId?: string) => {
    const url = courseId 
      ? `/admin/modules?course_id=${courseId}`
      : '/admin/modules';
    const response = await axios.get(url);
    return response.data;
  },

  createModule: async (moduleData: ModuleCreate) => {
    const response = await axios.post('/admin/modules', moduleData);
    return response.data;
  },

  getModule: async (moduleId: string) => {
    const response = await axios.get(`/admin/modules/${moduleId}`);
    return response.data;
  },

  updateModule: async (moduleId: string, moduleData: ModuleUpdate) => {
    const response = await axios.put(`/admin/modules/${moduleId}`, moduleData);
    return response.data;
  },

  deleteModule: async (moduleId: string) => {
    await axios.delete(`/admin/modules/${moduleId}`);
  },

  // Lessons
  getLesson: async (moduleId: string, lessonNumber: number): Promise<LessonContent> => {
    const response = await axios.get(`/admin/modules/${moduleId}/lessons/${lessonNumber}`);
    return response.data;
  },

  saveLesson: async (moduleId: string, lessonNumber: number, content: string) => {
    const formData = new FormData();
    formData.append('content', content);
    const response = await axios.post(
      `/admin/modules/${moduleId}/lessons/${lessonNumber}/content`,
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
    fileType: string,
    file: File
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    const response = await axios.post(
      `/admin/modules/${moduleId}/lessons/${lessonNumber}/files`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  listLessonFiles: async (moduleId: string, lessonNumber: number) => {
    const response = await axios.get(`/admin/modules/${moduleId}/lessons/${lessonNumber}/files`);
    return response.data;
  },

  getFileUrl: (moduleId: string, lessonNumber: number, fileType: string, filename: string) => {
    return `/api/v1/modules/${moduleId}/lessons/${lessonNumber}/files/${fileType}/${filename}`;
  },

  deleteFile: async (moduleId: string, lessonNumber: number, fileType: string, filename: string) => {
    await axios.delete(`/admin/modules/${moduleId}/lessons/${lessonNumber}/files/${fileType}/${filename}`);
  },

  // Tests
  getTest: async (moduleId: string) => {
    const response = await axios.get(`/admin/modules/${moduleId}/test`);
    return response.data;
  },

  saveTestQuestions: async (moduleId: string, testData: any) => {
    const response = await axios.post(`/admin/modules/${moduleId}/test/questions`, testData);
    return response.data;
  },

  saveTestSettings: async (moduleId: string, settingsData: any) => {
    const response = await axios.put(`/admin/modules/${moduleId}/test/settings`, settingsData);
    return response.data;
  },
};

