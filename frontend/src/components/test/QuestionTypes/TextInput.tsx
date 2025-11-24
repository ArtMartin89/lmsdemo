import React from 'react'

interface TextInputProps {
  question: {
    question_id: string
    question: string
    placeholder?: string
  }
  value: string
  onChange: (value: string) => void
}

const TextInput: React.FC<TextInputProps> = ({ question, value, onChange }) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={question.placeholder || 'Введите ответ'}
      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  )
}

export default TextInput


