'use client';

import { useInterviewStore } from '@/stores/interviewStore';
import { StatusBadge } from '@/components/ui/Badge';

export default function NumberCrossCheck() {
  const numbers = useInterviewStore((s) => s.numbers);

  return (
    <div className="p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        关键数字追踪
        {numbers.length > 0 && (
          <span className="bg-gray-200 text-gray-600 text-xs rounded-full px-2 py-0.5">{numbers.length}</span>
        )}
      </h3>

      {numbers.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">等待专家提及数字...</p>
      ) : (
        <div className="space-y-2">
          {numbers.map((num) => (
            <div
              key={num.id}
              className={`p-3 rounded-lg border text-sm ${
                num.verification === 'flagged'
                  ? 'border-red-200 bg-red-50'
                  : num.verification === 'consistent'
                  ? 'border-green-200 bg-green-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-gray-900">{num.value}</span>
                <StatusBadge status={num.verification} />
              </div>
              {num.context && <p className="text-xs text-gray-500 line-clamp-2">{num.context}</p>}
              {num.category && (
                <span className="inline-block mt-1 text-xs bg-gray-100 text-gray-600 rounded px-1.5 py-0.5">
                  {num.category}
                </span>
              )}
              {num.flag_reason && (
                <p className="text-xs text-red-600 mt-1 font-medium">{num.flag_reason}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
