import React from 'react'

interface MultipleChoiceProps {
  question: {
    question_id: string
    question: string
    options?: Array<{ id: string; text: string }>
  }
  value: string[]
  onChange: (value: string[]) => void
}

const MultipleChoice: React.FC<MultipleChoiceProps> = ({ question, value = [], onChange }) => {
  const handleToggle = (optionId: string) => {
    if (value.includes(optionId)) {
      onChange(value.filter(id => id !== optionId))
    } else {
      onChange([...value, optionId])
    }
  }

  return (
    <div className="space-y-2">
      {question.options?.map((option) => (
        <label
          key={option.id}
          className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
        >
          <input
            type="checkbox"
            checked={value.includes(option.id)}
            onChange={() => handleToggle(option.id)}
            className="mr-3"
          />
          <span>{option.text}</span>
        </label>
      ))}
    </div>
  )
}

export default MultipleChoice


