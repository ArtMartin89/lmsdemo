import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { adminApi } from '../../api/admin';
import Loading from '../../components/common/Loading';
import Button from '../../components/common/Button';

interface Question {
  question_id: string;
  type: 'single_choice' | 'multiple_choice' | 'text';
  question: string;
  options?: Array<{ id: string; text: string }>;
  points: number;
}

interface TestData {
  module_id: string;
  passing_threshold: number;
  time_limit_minutes: number;
  questions: Question[];
}

const AdminTestEditor: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const [testData, setTestData] = useState<TestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (moduleId) {
      loadTest();
    }
  }, [moduleId]);

  const loadTest = async () => {
    try {
      const data = await adminApi.getTest(moduleId!);
      setTestData(data);
    } catch (error) {
      console.error('Failed to load test:', error);
      // Initialize empty test if not found
      setTestData({
        module_id: moduleId!,
        passing_threshold: 0.7,
        time_limit_minutes: 30,
        questions: []
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!testData) return;
    
    setSaving(true);
    try {
      await adminApi.saveTest(moduleId!, testData);
      alert('Тест сохранен успешно!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не удалось сохранить тест');
    } finally {
      setSaving(false);
    }
  };

  const addQuestion = () => {
    if (!testData) return;
    
    const newQuestion: Question = {
      question_id: `q${testData.questions.length + 1}`,
      type: 'single_choice',
      question: '',
      options: [
        { id: 'A', text: '' },
        { id: 'B', text: '' },
        { id: 'C', text: '' }
      ],
      points: 1
    };
    
    setTestData({
      ...testData,
      questions: [...testData.questions, newQuestion]
    });
  };

  const removeQuestion = (index: number) => {
    if (!testData) return;
    
    const newQuestions = testData.questions.filter((_, i) => i !== index);
    setTestData({ ...testData, questions: newQuestions });
  };

  const updateQuestion = (index: number, field: string, value: any) => {
    if (!testData) return;
    
    const newQuestions = [...testData.questions];
    (newQuestions[index] as any)[field] = value;
    setTestData({ ...testData, questions: newQuestions });
  };

  const addOption = (questionIndex: number) => {
    if (!testData) return;
    
    const newQuestions = [...testData.questions];
    const question = newQuestions[questionIndex];
    if (question.options) {
      const nextId = String.fromCharCode(65 + question.options.length);
      question.options.push({ id: nextId, text: '' });
      setTestData({ ...testData, questions: newQuestions });
    }
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    if (!testData) return;
    
    const newQuestions = [...testData.questions];
    const question = newQuestions[questionIndex];
    if (question.options) {
      question.options = question.options.filter((_, i) => i !== optionIndex);
      setTestData({ ...testData, questions: newQuestions });
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (!testData) {
    return <div>Test not found</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button onClick={() => navigate(`/admin/modules/${moduleId}/lessons`)} variant="secondary">
          ← Назад к урокам
        </Button>
        <h1 className="text-3xl font-bold mt-4">Редактирование теста модуля {moduleId}</h1>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Порог прохождения (0-1)</label>
            <input
              type="number"
              value={testData.passing_threshold}
              onChange={(e) => setTestData({ ...testData, passing_threshold: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border rounded"
              min="0"
              max="1"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Лимит времени (минуты)</label>
            <input
              type="number"
              value={testData.time_limit_minutes}
              onChange={(e) => setTestData({ ...testData, time_limit_minutes: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border rounded"
              min="1"
            />
          </div>
        </div>
      </div>

      <div className="mb-4">
        <Button onClick={addQuestion}>Добавить вопрос</Button>
        <Button onClick={handleSave} disabled={saving} className="ml-2">
          {saving ? 'Сохранение...' : 'Сохранить тест'}
        </Button>
      </div>

      <div className="space-y-4">
        {testData.questions.map((question, qIndex) => (
          <div key={qIndex} className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Вопрос {qIndex + 1}</h3>
              <Button onClick={() => removeQuestion(qIndex)} variant="danger">
                Удалить
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Тип вопроса</label>
                <select
                  value={question.type}
                  onChange={(e) => updateQuestion(qIndex, 'type', e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="single_choice">Один вариант</option>
                  <option value="multiple_choice">Несколько вариантов</option>
                  <option value="text">Текстовый ответ</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Текст вопроса</label>
                <textarea
                  value={question.question}
                  onChange={(e) => updateQuestion(qIndex, 'question', e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                  rows={3}
                />
              </div>

              {question.type !== 'text' && question.options && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium">Варианты ответов</label>
                    <Button onClick={() => addOption(qIndex)} variant="secondary" type="button">
                      Добавить вариант
                    </Button>
                  </div>
                  {question.options.map((option, oIndex) => (
                    <div key={oIndex} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={option.id}
                        disabled
                        className="w-12 px-2 py-2 border rounded"
                      />
                      <input
                        type="text"
                        value={option.text}
                        onChange={(e) => {
                          const newQuestions = [...testData.questions];
                          if (newQuestions[qIndex].options) {
                            newQuestions[qIndex].options![oIndex].text = e.target.value;
                            setTestData({ ...testData, questions: newQuestions });
                          }
                        }}
                        className="flex-1 px-3 py-2 border rounded"
                        placeholder="Текст варианта ответа"
                      />
                      <Button
                        onClick={() => removeOption(qIndex, oIndex)}
                        variant="danger"
                        type="button"
                      >
                        Удалить
                      </Button>
                    </div>
                  ))}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-1">Баллы</label>
                <input
                  type="number"
                  value={question.points}
                  onChange={(e) => updateQuestion(qIndex, 'points', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border rounded"
                  min="1"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminTestEditor;

