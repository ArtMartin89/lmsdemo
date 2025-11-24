import React from 'react'

interface SingleChoiceProps {
  question: {
    question_id: string
    question: string
    options?: Array<{ id: string; text: string }>
  }
  value: string | undefined
  onChange: (value: string) => void
}

const SingleChoice: React.FC<SingleChoiceProps> = ({ question, value, onChange }) => {
  return (
    <div className="space-y-2">
      {question.options?.map((option) => (
        <label
          key={option.id}
          className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
        >
          <input
            type="radio"
            name={question.question_id}
            value={option.id}
            checked={value === option.id}
            onChange={(e) => onChange(e.target.value)}
            className="mr-3"
          />
          <span>{option.text}</span>
        </label>
      ))}
    </div>
  )
}

export default SingleChoice


