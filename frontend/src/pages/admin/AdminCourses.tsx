import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminApi, CourseCreate, Course } from '../../api/admin';
import Loading from '../../components/common/Loading';
import Button from '../../components/common/Button';

const AdminCourses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await adminApi.listCourses();
      setCourses(data);
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (courseData: CourseCreate) => {
    try {
      await adminApi.createCourse(courseData);
      setShowCreateForm(false);
      loadCourses();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create course');
    }
  };

  const handleUpdate = async (courseId: string, courseData: any) => {
    try {
      await adminApi.updateCourse(courseId, courseData);
      setEditingCourse(null);
      loadCourses();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update course');
    }
  };

  const handleDelete = async (courseId: string) => {
    if (!confirm('Are you sure you want to delete this course? All modules will be deleted too.')) {
      return;
    }
    try {
      await adminApi.deleteCourse(courseId);
      loadCourses();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete course');
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Управление курсами</h1>
        <Button onClick={() => setShowCreateForm(true)}>Создать курс</Button>
      </div>

      {showCreateForm && (
        <CourseForm
          onSubmit={handleCreate}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      <div className="grid gap-4">
        {courses.map((course) => (
          <div key={course.id} className="bg-white rounded-lg shadow p-6">
            {editingCourse?.id === course.id ? (
              <CourseForm
                course={course}
                onSubmit={(data) => handleUpdate(course.id, data)}
                onCancel={() => setEditingCourse(null)}
              />
            ) : (
              <>
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold">{course.title}</h2>
                    <p className="text-gray-600 mt-2">{course.description}</p>
                    <div className="mt-4 text-sm text-gray-500">
                      <span>Порядок: {course.order_index}</span>
                      <span className="ml-4">
                        Статус: {course.is_active ? 'Активен' : 'Неактивен'}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => navigate(`/admin/courses/${course.id}/modules`)}
                      variant="secondary"
                    >
                      Модули
                    </Button>
                    <Button
                      onClick={() => setEditingCourse(course)}
                      variant="secondary"
                    >
                      Редактировать
                    </Button>
                    <Button
                      onClick={() => handleDelete(course.id)}
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

interface CourseFormProps {
  course?: Course;
  onSubmit: (data: CourseCreate | any) => void;
  onCancel: () => void;
}

const CourseForm: React.FC<CourseFormProps> = ({ course, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: course?.title || '',
    description: course?.description || '',
    order_index: course?.order_index || 0,
    is_active: course?.is_active ?? true,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-gray-50 p-4 rounded-lg mb-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="block text-sm font-medium mb-1">Название курса</label>
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
          <label className="block text-sm font-medium mb-1">Порядок</label>
          <input
            type="number"
            value={formData.order_index}
            onChange={(e) => setFormData({ ...formData, order_index: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded"
            min="0"
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

export default AdminCourses;

