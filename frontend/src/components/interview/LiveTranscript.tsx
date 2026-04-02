'use client';

import { useEffect, useRef } from 'react';
import { useInterviewStore } from '@/stores/interviewStore';

export default function LiveTranscript() {
  const segments = useInterviewStore((s) => s.segments);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [segments]);

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
      {segments.length === 0 ? (
        <div className="text-center text-gray-400 py-20">
          <p className="text-lg">等待访谈开始...</p>
          <p className="text-sm mt-2">点击录音按钮开始录制访谈</p>
        </div>
      ) : (
        segments.map((seg, i) => (
          <div key={i} className="flex gap-3">
            <div className="flex-shrink-0 mt-1">
              <span
                className={`inline-block w-8 h-8 rounded-full text-center leading-8 text-xs font-medium ${
                  seg.speaker === 'expert' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                }`}
              >
                {seg.speaker === 'expert' ? '专' : '研'}
              </span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-medium text-gray-500">
                  {seg.speaker === 'expert' ? '专家' : '研究员'}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(seg.start_time_ms)}
                </span>
              </div>
              <p className="text-sm text-gray-800 leading-relaxed">{seg.text}</p>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}
