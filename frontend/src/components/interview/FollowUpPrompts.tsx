'use client';

import { useInterviewStore } from '@/stores/interviewStore';
import Badge from '@/components/ui/Badge';

export default function FollowUpPrompts() {
  const prompts = useInterviewStore((s) => s.prompts);
  const dismissPrompt = useInterviewStore((s) => s.dismissPrompt);

  return (
    <div className="p-4 space-y-3">
      <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
        JIT 追问建议
        {prompts.length > 0 && (
          <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-0.5">{prompts.length}</span>
        )}
      </h3>

      {prompts.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">等待AI生成追问建议...</p>
      ) : (
        prompts.map((prompt, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg border ${
              prompt.priority === 'high'
                ? 'border-red-200 bg-red-50'
                : prompt.priority === 'medium'
                ? 'border-yellow-200 bg-yellow-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge
                    variant={
                      prompt.priority === 'high' ? 'danger' : prompt.priority === 'medium' ? 'warning' : 'default'
                    }
                  >
                    {prompt.priority === 'high' ? '高优' : prompt.priority === 'medium' ? '中优' : '低优'}
                  </Badge>
                  {prompt.trigger && <span className="text-xs text-gray-400">{prompt.trigger}</span>}
                </div>
                <p className="text-sm text-gray-800 font-medium mt-1">{prompt.text}</p>
                <p className="text-xs text-gray-500 mt-1">{prompt.rationale}</p>
              </div>
              <button
                onClick={() => dismissPrompt(i)}
                className="text-gray-400 hover:text-gray-600 text-sm flex-shrink-0"
              >
                x
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
