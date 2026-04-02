import { create } from 'zustand';
import type {
  TranscriptSegment,
  NumberRecord,
  FollowUpPrompt,
  CredibilityResult,
} from '@/lib/types';

interface InterviewState {
  // Transcript
  segments: TranscriptSegment[];
  addSegment: (seg: TranscriptSegment) => void;

  // Numbers
  numbers: NumberRecord[];
  addNumber: (num: NumberRecord) => void;
  updateNumber: (id: string, data: Partial<NumberRecord>) => void;

  // Follow-up prompts
  prompts: FollowUpPrompt[];
  setPrompts: (prompts: FollowUpPrompt[]) => void;
  dismissPrompt: (index: number) => void;

  // Credibility
  credibility: CredibilityResult | null;
  setCredibility: (result: CredibilityResult) => void;

  // Connection
  isConnected: boolean;
  setConnected: (connected: boolean) => void;

  // Recording
  isRecording: boolean;
  setRecording: (recording: boolean) => void;

  // Timer
  elapsedSeconds: number;
  setElapsedSeconds: (seconds: number) => void;

  // Reset
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  segments: [],
  addSegment: (seg) => set((s) => ({ segments: [...s.segments, seg] })),

  numbers: [],
  addNumber: (num) => set((s) => ({ numbers: [...s.numbers, num] })),
  updateNumber: (id, data) =>
    set((s) => ({
      numbers: s.numbers.map((n) => (n.id === id ? { ...n, ...data } : n)),
    })),

  prompts: [],
  setPrompts: (prompts) => set({ prompts }),
  dismissPrompt: (index) =>
    set((s) => ({ prompts: s.prompts.filter((_, i) => i !== index) })),

  credibility: null,
  setCredibility: (result) => set({ credibility: result }),

  isConnected: false,
  setConnected: (connected) => set({ isConnected: connected }),

  isRecording: false,
  setRecording: (recording) => set({ isRecording: recording }),

  elapsedSeconds: 0,
  setElapsedSeconds: (seconds) => set({ elapsedSeconds: seconds }),

  reset: () =>
    set({
      segments: [],
      numbers: [],
      prompts: [],
      credibility: null,
      isConnected: false,
      isRecording: false,
      elapsedSeconds: 0,
    }),
}));
