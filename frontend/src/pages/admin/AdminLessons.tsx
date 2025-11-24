import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi } from '../../api/admin';
import Loading from '../../components/common/Loading';
import Button from '../../components/common/Button';

const AdminLessons: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState<number[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (moduleId) {
      loadModuleInfo();
    }
  }, [moduleId]);

  const loadModuleInfo = async () => {
    try {
      const module = await adminApi.getModule(moduleId!);
      const lessonNumbers = Array.from({ length: module.total_lessons }, (_, i) => i + 1);
      setLessons(lessonNumbers);
    } catch (error) {
      console.error('Failed to load module:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button onClick={() => navigate('/admin/modules')} variant="secondary">
          ← Назад к модулям
        </Button>
        <h1 className="text-3xl font-bold mt-4">Управление уроками модуля {moduleId}</h1>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-1">
          <h2 className="text-xl font-semibold mb-4">Уроки</h2>
          <div className="space-y-2">
            {lessons.map((lessonNum) => (
              <button
                key={lessonNum}
                onClick={() => setSelectedLesson(lessonNum)}
                className={`w-full text-left px-4 py-2 rounded ${
                  selectedLesson === lessonNum
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 hover:bg-gray-200'
                }`}
              >
                Урок {lessonNum}
              </button>
            ))}
          </div>
        </div>

        <div className="col-span-3">
          {selectedLesson ? (
            <LessonEditor
              moduleId={moduleId!}
              lessonNumber={selectedLesson}
              onBack={() => setSelectedLesson(null)}
            />
          ) : (
            <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
              Выберите урок для редактирования
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface LessonEditorProps {
  moduleId: string;
  lessonNumber: number;
  onBack: () => void;
}

const LessonEditor: React.FC<LessonEditorProps> = ({
  moduleId,
  lessonNumber,
  onBack,
}) => {
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadLesson();
  }, [moduleId, lessonNumber]);

  const loadLesson = async () => {
    try {
      const lesson = await adminApi.getLesson(moduleId, lessonNumber);
      setContent(lesson.content || '');
      setFiles(lesson.files || []);
    } catch (error: any) {
      // If lesson doesn't exist, create empty content
      if (error.response?.status === 404) {
        setContent('');
        setFiles([]);
      } else {
        console.error('Failed to load lesson:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await adminApi.saveLesson(moduleId, lessonNumber, content);
      alert('Урок сохранен успешно!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не удалось сохранить урок');
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await adminApi.uploadFile(moduleId, lessonNumber, file);
      await loadLesson(); // Reload to get updated file list
      alert('Файл загружен успешно!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не удалось загрузить файл');
    } finally {
      setUploading(false);
      e.target.value = ''; // Reset input
    }
  };

  const handleDeleteFile = async (filename: string) => {
    if (!confirm(`Удалить файл ${filename}?`)) return;
    try {
      await adminApi.deleteFile(moduleId, lessonNumber, filename);
      await loadLesson();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не удалось удалить файл');
    }
  };

  const getFileType = (filename: string): 'audio' | 'video' | 'image' | 'other' => {
    const ext = filename.toLowerCase().split('.').pop();
    if (['mp3', 'wav', 'ogg'].includes(ext || '')) return 'audio';
    if (['mp4', 'webm'].includes(ext || '')) return 'video';
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) return 'image';
    return 'other';
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Урок {lessonNumber}</h2>
        <div className="flex gap-2">
          <Button onClick={onBack} variant="secondary">
            Назад
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </div>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Содержание урока (Markdown)</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full px-3 py-2 border rounded font-mono"
          rows={20}
          placeholder="Введите содержимое урока в формате Markdown..."
        />
      </div>

      <div className="border-t pt-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Файлы урока</h3>
          <label className="cursor-pointer">
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
              accept="audio/*,video/*,image/*"
            />
            <Button as="span" disabled={uploading}>
              {uploading ? 'Загрузка...' : 'Загрузить файл'}
            </Button>
          </label>
        </div>

        {files.length === 0 ? (
          <p className="text-gray-500">Нет загруженных файлов</p>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {files.map((filename) => {
              const fileType = getFileType(filename);
              const fileUrl = adminApi.getFileUrl(moduleId, lessonNumber, filename);

              return (
                <div key={filename} className="border rounded p-4">
                  <div className="mb-2">
                    {fileType === 'audio' && (
                      <audio controls className="w-full">
                        <source src={fileUrl} />
                      </audio>
                    )}
                    {fileType === 'video' && (
                      <video controls className="w-full">
                        <source src={fileUrl} />
                      </video>
                    )}
                    {fileType === 'image' && (
                      <img src={fileUrl} alt={filename} className="w-full h-32 object-cover rounded" />
                    )}
                    {fileType === 'other' && (
                      <div className="bg-gray-100 p-4 text-center text-gray-500">
                        {filename}
                      </div>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 truncate">{filename}</p>
                  <Button
                    onClick={() => handleDeleteFile(filename)}
                    variant="danger"
                    className="mt-2 w-full text-sm"
                  >
                    Удалить
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="border-t pt-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Тест модуля</h3>
          <Button
            onClick={() => navigate(`/admin/modules/${moduleId}/test`)}
            variant="secondary"
          >
            Редактировать тест
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AdminLessons;

