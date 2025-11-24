import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi, ModuleCreate, CourseWithModules } from '../../api/admin';
import Loading from '../../components/common/Loading';
import Button from '../../components/common/Button';

interface Module {
  id: string;
  title: string;
  description?: string;
  total_lessons: number;
  order_index: number;
  is_active: boolean;
}

const AdminCourseModules: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<CourseWithModules | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingModule, setEditingModule] = useState<Module | null>(null);

  useEffect(() => {
    if (courseId) {
      loadCourse();
    }
  }, [courseId]);

  const loadCourse = async () => {
    try {
      const data = await adminApi.getCourse(courseId!);
      setCourse(data);
    } catch (error) {
      console.error('Failed to load course:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (moduleData: ModuleCreate) => {
    try {
      await adminApi.createModule(moduleData);
      setShowCreateForm(false);
      loadCourse();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create module');
    }
  };

  const handleUpdate = async (moduleId: string, moduleData: any) => {
    try {
      await adminApi.updateModule(moduleId, moduleData);
      setEditingModule(null);
      loadCourse();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update module');
    }
  };

  const handleDelete = async (moduleId: string) => {
    if (!confirm('Are you sure you want to delete this module?')) {
      return;
    }
    try {
      await adminApi.deleteModule(moduleId);
      loadCourse();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete module');
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (!course) {
    return <div>Course not found</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button onClick={() => navigate('/admin/courses')} variant="secondary">
          ← Назад к курсам
        </Button>
        <h1 className="text-3xl font-bold mt-4">
          Модули курса: {course.title}
        </h1>
      </div>

      <div className="flex justify-between items-center mb-6">
        <p className="text-gray-600">{course.description}</p>
        <Button onClick={() => setShowCreateForm(true)}>Создать модуль</Button>
      </div>

      {showCreateForm && (
        <ModuleForm
          courseId={courseId!}
          onSubmit={handleCreate}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      <div className="grid gap-4">
        {course.modules.map((module) => (
          <div key={module.id} className="bg-white rounded-lg shadow p-6">
            {editingModule?.id === module.id ? (
              <ModuleForm
                courseId={courseId!}
                module={module}
                onSubmit={(data) => handleUpdate(module.id, data)}
                onCancel={() => setEditingModule(null)}
              />
            ) : (
              <>
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold">{module.title}</h2>
                    <p className="text-gray-600 mt-2">{module.description}</p>
                    <div className="mt-4 text-sm text-gray-500">
                      <span>Уроков: {module.total_lessons}</span>
                      <span className="ml-4">Порядок: {module.order_index}</span>
                      <span className="ml-4">
                        Статус: {module.is_active ? 'Активен' : 'Неактивен'}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => navigate(`/admin/modules/${module.id}/lessons`)}
                      variant="secondary"
                    >
                      Уроки
                    </Button>
                    <Button
                      onClick={() => setEditingModule(module)}
                      variant="secondary"
                    >
                      Редактировать
                    </Button>
                    <Button
                      onClick={() => handleDelete(module.id)}
                      variant="danger"
                    >
                      Удалить
                    </Button>
                  </div>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

interface ModuleFormProps {
  courseId: string;
  module?: Module;
  onSubmit: (data: ModuleCreate | any) => void;
  onCancel: () => void;
}

const ModuleForm: React.FC<ModuleFormProps> = ({ courseId, module, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    id: module?.id || '',
    course_id: courseId,
    title: module?.title || '',
    description: module?.description || '',
    total_lessons: module?.total_lessons || 3,
    order_index: module?.order_index || 1,
    is_active: module?.is_active ?? true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-50 p-4 rounded-lg mb-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">ID модуля</label>
          <input
            type="text"
            value={formData.id}
            onChange={(e) => setFormData({ ...formData, id: e.target.value })}
            className="w-full px-3 py-2 border rounded"
            required
            disabled={!!module}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Название</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Описание</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border rounded"
            rows={3}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Количество уроков</label>
          <input
            type="number"
            value={formData.total_lessons}
            onChange={(e) => setFormData({ ...formData, total_lessons: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded"
            min="1"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Порядок</label>
          <input
            type="number"
            value={formData.order_index}
            onChange={(e) => setFormData({ ...formData, order_index: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded"
            min="1"
            required
          />
        </div>
        <div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            />
            <span>Активен</span>
          </label>
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        <Button type="submit">Сохранить</Button>
        <Button type="button" onClick={onCancel} variant="secondary">
          Отмена
        </Button>
      </div>
    </form>
  );
};

export default AdminCourseModules;

