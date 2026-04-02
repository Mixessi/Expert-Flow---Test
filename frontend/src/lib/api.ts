import axios from 'axios';
import type {
  Project,
  Interview,
  Outline,
  ResearchResult,
  ReferenceDocument,
  Note,
  TranscriptSegment,
  NumberRecord,
} from './types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});

// Projects
export const createProject = (data: Partial<Project>) =>
  api.post<Project>('/projects', data).then((r) => r.data);

export const listProjects = () =>
  api.get<Project[]>('/projects').then((r) => r.data);

export const getProject = (id: string) =>
  api.get<Project>(`/projects/${id}`).then((r) => r.data);

export const updateProject = (id: string, data: Partial<Project>) =>
  api.put<Project>(`/projects/${id}`, data).then((r) => r.data);

export const deleteProject = (id: string) =>
  api.delete(`/projects/${id}`).then((r) => r.data);

// Interviews
export const createInterview = (projectId: string, data: Partial<Interview>) =>
  api.post<Interview>(`/projects/${projectId}/interviews`, data).then((r) => r.data);

export const listInterviews = (projectId: string) =>
  api.get<Interview[]>(`/projects/${projectId}/interviews`).then((r) => r.data);

export const getInterview = (id: string) =>
  api.get<Interview>(`/interviews/${id}`).then((r) => r.data);

export const updateInterview = (id: string, data: Partial<Interview>) =>
  api.put<Interview>(`/interviews/${id}`, data).then((r) => r.data);

export const startInterview = (id: string) =>
  api.post<Interview>(`/interviews/${id}/start`).then((r) => r.data);

export const endInterview = (id: string) =>
  api.post<Interview>(`/interviews/${id}/end`).then((r) => r.data);

// Research
export const startResearch = (interviewId: string, query: string) =>
  api.post<ResearchResult>(`/interviews/${interviewId}/research/start`, { query }).then((r) => r.data);

export const getResearch = (interviewId: string) =>
  api.get<ResearchResult[]>(`/interviews/${interviewId}/research`).then((r) => r.data);

// Documents
export const uploadDocument = (interviewId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<ReferenceDocument>(`/interviews/${interviewId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data);
};

export const listDocuments = (interviewId: string) =>
  api.get<ReferenceDocument[]>(`/interviews/${interviewId}/documents`).then((r) => r.data);

export const deleteDocument = (id: string) =>
  api.delete(`/documents/${id}`).then((r) => r.data);

// Outlines
export const generateOutline = (interviewId: string, feedback?: string) =>
  api.post<Outline>(`/interviews/${interviewId}/outline/generate`, feedback ? { feedback } : {}).then((r) => r.data);

export const getOutline = (interviewId: string) =>
  api.get<Outline>(`/interviews/${interviewId}/outline`).then((r) => r.data);

export const updateOutline = (outlineId: string, content: object) =>
  api.put<Outline>(`/outlines/${outlineId}`, { content }).then((r) => r.data);

// Notes
export const generateNotes = (interviewId: string) =>
  api.post<Note>(`/interviews/${interviewId}/notes/generate`).then((r) => r.data);

export const getNotes = (interviewId: string) =>
  api.get<Note>(`/interviews/${interviewId}/notes`).then((r) => r.data);

export const updateNotes = (interviewId: string, data: Partial<Note>) =>
  api.put<Note>(`/interviews/${interviewId}/notes`, data).then((r) => r.data);

// Transcript & Numbers
export const getTranscript = (interviewId: string) =>
  api.get<TranscriptSegment[]>(`/interviews/${interviewId}/transcript`).then((r) => r.data);

export const getNumbers = (interviewId: string) =>
  api.get<NumberRecord[]>(`/interviews/${interviewId}/numbers`).then((r) => r.data);
