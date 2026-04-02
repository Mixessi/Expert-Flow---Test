'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getInterview, endInterview } from '@/lib/api';
import type { Interview, WSMessage, TranscriptSegment, NumberRecord, FollowUpPrompt, CredibilityResult } from '@/lib/types';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useInterviewStore } from '@/stores/interviewStore';
import Header from '@/components/layout/Header';
import AudioControls from '@/components/interview/AudioControls';
import LiveTranscript from '@/components/interview/LiveTranscript';
import FollowUpPrompts from '@/components/interview/FollowUpPrompts';
import NumberCrossCheck from '@/components/interview/NumberCrossCheck';
import CredibilityGauge from '@/components/interview/CredibilityGauge';
import Button from '@/components/ui/Button';

type TabName = 'followup' | 'numbers' | 'credibility';

export default function LiveInterviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;
  const interviewId = params.interviewId as string;

  const [interview, setInterview] = useState<Interview | null>(null);
  const [activeTab, setActiveTab] = useState<TabName>('followup');
  const [ending, setEnding] = useState(false);

  const store = useInterviewStore();
  const timerRef = useRef<NodeJS.Timeout>();

  // Load interview data
  useEffect(() => {
    getInterview(interviewId).then(setInterview).catch(console.error);
    store.reset();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [interviewId]);

  // WebSocket message handler
  const handleWSMessage = useCallback((msg: WSMessage) => {
    switch (msg.type) {
      case 'transcript_segment':
        store.addSegment(msg.data as TranscriptSegment);
        break;
      case 'number_extracted':
        store.addNumber(msg.data as NumberRecord);
        break;
      case 'followup_prompt': {
        const data = msg.data as { prompts: FollowUpPrompt[] };
        store.setPrompts(data.prompts);
        break;
      }
      case 'number_flag': {
        const flagData = msg.data as { checks?: Array<{ number_id: string; verification: string; reason: string }> };
        flagData.checks?.forEach((check) => {
          store.updateNumber(check.number_id, {
            verification: check.verification as NumberRecord['verification'],
            flag_reason: check.reason,
          });
        });
        break;
      }
      case 'credibility_update':
        store.setCredibility(msg.data as CredibilityResult);
        break;
      case 'error':
        console.error('WS error:', msg.data);
        break;
    }
  }, []);

  const wsUrl = typeof window !== 'undefined'
    ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//localhost:8000/api/v1/ws/interview/${interviewId}`
    : null;

  const { isConnected, sendMessage } = useWebSocket(wsUrl, {
    onMessage: handleWSMessage,
    onOpen: () => store.setConnected(true),
    onClose: () => store.setConnected(false),
  });

  // Audio recorder
  const { isRecording, startRecording, stopRecording } = useAudioRecorder({
    onChunk: (base64Audio) => {
      sendMessage({ type: 'audio_chunk', data: base64Audio });
    },
  });

  const handleStart = () => {
    startRecording();
    store.setRecording(true);
    timerRef.current = setInterval(() => {
      store.setElapsedSeconds(store.elapsedSeconds + 1);
    }, 1000);
  };

  const handleStop = () => {
    stopRecording();
    store.setRecording(false);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const handleEndInterview = async () => {
    if (!confirm('确定结束访谈？结束后将自动生成访谈纪要。')) return;
    setEnding(true);
    handleStop();
    try {
      await endInterview(interviewId);
      router.push(`/projects/${projectId}/interviews/${interviewId}/notes`);
    } catch (error) {
      console.error(error);
    } finally {
      setEnding(false);
    }
  };

  const tabs: { key: TabName; label: string; count?: number }[] = [
    { key: 'followup', label: 'JIT 追问', count: store.prompts.length },
    { key: 'numbers', label: '数字追踪', count: store.numbers.length },
    { key: 'credibility', label: '可信度' },
  ];

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="font-semibold text-gray-900">{interview?.expert_name || '实时访谈'}</h2>
            <p className="text-xs text-gray-500">
              {interview?.expert_company} {interview?.expert_title}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <AudioControls
            isRecording={isRecording}
            isConnected={isConnected}
            elapsedSeconds={store.elapsedSeconds}
            onStart={handleStart}
            onStop={handleStop}
          />
          <Button variant="danger" size="sm" onClick={handleEndInterview} loading={ending}>
            结束访谈
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Live Transcript */}
        <div className="w-1/2 border-r flex flex-col bg-white">
          <div className="px-4 py-2 border-b bg-gray-50">
            <h3 className="text-sm font-medium text-gray-600">实时转录</h3>
          </div>
          <LiveTranscript />
        </div>

        {/* Right: Analysis Panels */}
        <div className="w-1/2 flex flex-col bg-white">
          {/* Tabs */}
          <div className="flex border-b bg-gray-50">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex-1 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600 bg-white'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <span className="ml-1.5 bg-blue-100 text-blue-600 text-xs rounded-full px-1.5 py-0.5">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'followup' && <FollowUpPrompts />}
            {activeTab === 'numbers' && <NumberCrossCheck />}
            {activeTab === 'credibility' && <CredibilityGauge />}
          </div>
        </div>
      </div>
    </div>
  );
}
