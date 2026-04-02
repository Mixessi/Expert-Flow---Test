'use client';

import { useInterviewStore } from '@/stores/interviewStore';

export default function CredibilityGauge() {
  const credibility = useInterviewStore((s) => s.credibility);

  if (!credibility) {
    return (
      <div className="p-4 text-center">
        <p className="text-sm text-gray-400 py-8">可信度评估将在访谈开始 1 分钟后启动...</p>
      </div>
    );
  }

  const scorePercent = Math.round(credibility.score * 100);
  const levelConfig = {
    high: { label: '高可信度', color: 'text-green-600', bg: 'bg-green-500' },
    medium: { label: '中等可信度', color: 'text-yellow-600', bg: 'bg-yellow-500' },
    low: { label: '低可信度', color: 'text-orange-600', bg: 'bg-orange-500' },
    concerning: { label: '可信度存疑', color: 'text-red-600', bg: 'bg-red-500' },
  };

  const config = levelConfig[credibility.level] || levelConfig.medium;

  return (
    <div className="p-4 space-y-4">
      <div className="text-center">
        <div className="relative w-24 h-24 mx-auto">
          <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15" fill="none" stroke="#e5e7eb" strokeWidth="3" />
            <circle
              cx="18"
              cy="18"
              r="15"
              fill="none"
              className={config.bg.replace('bg-', 'stroke-')}
              strokeWidth="3"
              strokeDasharray={`${scorePercent} 100`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-xl font-bold ${config.color}`}>{scorePercent}</span>
          </div>
        </div>
        <p className={`mt-2 text-sm font-medium ${config.color}`}>{config.label}</p>
      </div>

      {credibility.factors.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-500 uppercase">评估维度</h4>
          {credibility.factors.map((factor, i) => (
            <div key={i} className="text-sm">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-700">{factor.dimension}</span>
                <span className="text-gray-500">{Math.round(factor.score * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${
                    factor.score >= 0.7 ? 'bg-green-500' : factor.score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${factor.score * 100}%` }}
                />
              </div>
              {factor.concern && <p className="text-xs text-red-500 mt-0.5">{factor.concern}</p>}
            </div>
          ))}
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-xs font-medium text-blue-700">建议</p>
        <p className="text-sm text-blue-600 mt-1">{credibility.recommendation}</p>
      </div>
    </div>
  );
}
