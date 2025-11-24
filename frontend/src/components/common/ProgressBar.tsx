import React from 'react'

interface ProgressBarProps {
  current: number
  total: number
  percentage?: number
}

const ProgressBar: React.FC<ProgressBarProps> = ({ current, total, percentage }) => {
  const progressPercentage = percentage ?? (total > 0 ? Math.round((current / total) * 100) : 0)

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          Прогресс: {current} из {total}
        </span>
        <span className="text-sm font-medium text-gray-700">{progressPercentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>
    </div>
  )
}

export default ProgressBar


