'use client';

import Button from '@/components/ui/Button';

interface AudioControlsProps {
  isRecording: boolean;
  isConnected: boolean;
  elapsedSeconds: number;
  onStart: () => void;
  onStop: () => void;
}

export default function AudioControls({
  isRecording,
  isConnected,
  elapsedSeconds,
  onStart,
  onStop,
}: AudioControlsProps) {
  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center gap-4">
      {/* Connection indicator */}
      <div className="flex items-center gap-2 text-sm">
        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-gray-500">{isConnected ? '已连接' : '未连接'}</span>
      </div>

      {/* Timer */}
      <div className="font-mono text-lg font-semibold text-gray-700 tabular-nums">
        {formatTime(elapsedSeconds)}
      </div>

      {/* Record button */}
      {isRecording ? (
        <Button variant="danger" onClick={onStop}>
          <span className="w-3 h-3 bg-white rounded-sm mr-2" />
          停止录音
        </Button>
      ) : (
        <Button variant="primary" onClick={onStart} disabled={!isConnected}>
          <span className="w-3 h-3 bg-white rounded-full mr-2 animate-pulse" />
          开始录音
        </Button>
      )}
    </div>
  );
}
