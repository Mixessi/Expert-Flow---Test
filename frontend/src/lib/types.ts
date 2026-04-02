export interface Project {
  id: string;
  name: string;
  description: string | null;
  research_goals: string | null;
  industry: string | null;
  created_at: string;
  updated_at: string;
}

export interface Interview {
  id: string;
  project_id: string;
  expert_name: string | null;
  expert_title: string | null;
  expert_company: string | null;
  expert_bio: string | null;
  core_questions: string | null;
  status: 'draft' | 'scheduled' | 'live' | 'completed';
  scheduled_at: string | null;
  started_at: string | null;
  ended_at: string | null;
  credibility_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface OutlineQuestion {
  text: string;
  rationale: string;
  priority: 'high' | 'medium' | 'low';
  type: 'test_question' | 'core' | 'follow_up';
  expected_info?: string;
}

export interface OutlineSection {
  title: string;
  purpose: string;
  questions: OutlineQuestion[];
}

export interface OutlineContent {
  sections: OutlineSection[];
  estimated_duration_minutes?: number;
  key_hypotheses?: string[];
  raw_text?: string;
}

export interface Outline {
  id: string;
  interview_id: string;
  version: number;
  content: OutlineContent;
  is_active: boolean;
  created_at: string;
}

export interface ResearchResult {
  id: string;
  interview_id: string;
  query: string;
  status: string;
  company_overview: string | null;
  industry_data: string | null;
  key_numbers: Array<{ metric: string; value: string; source: string; date: string }> | null;
  info_gaps: string[] | null;
  created_at: string;
}

export interface ReferenceDocument {
  id: string;
  interview_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  extracted_text: string | null;
  created_at: string;
}

export interface TranscriptSegment {
  id?: string;
  segment_index: number;
  speaker: string | null;
  text: string;
  start_time_ms: number;
  end_time_ms: number;
  confidence?: number;
}

export interface NumberRecord {
  id: string;
  interview_id?: string;
  value: string;
  normalized?: number;
  unit?: string;
  context: string | null;
  category: string | null;
  verification: 'unverified' | 'consistent' | 'flagged';
  flag_reason?: string | null;
  created_at?: string;
}

export interface FollowUpPrompt {
  text: string;
  rationale: string;
  priority: 'high' | 'medium' | 'low';
  trigger?: string;
}

export interface CredibilityResult {
  score: number;
  level: 'high' | 'medium' | 'low' | 'concerning';
  factors: Array<{
    dimension: string;
    score: number;
    evidence: string;
    concern?: string;
  }>;
  recommendation: string;
}

export interface Note {
  id: string;
  interview_id: string;
  summary: string | null;
  key_insights: Array<{ insight: string; supporting_quote: string; confidence: string }> | null;
  full_notes: string | null;
  key_numbers: Array<{
    value: string;
    context: string;
    category: string;
    verification: string;
    flag_reason?: string;
  }> | null;
  action_items: Array<{ item: string; assignee?: string; deadline?: string }> | null;
  generated_at: string;
  updated_at: string;
}

// WebSocket message types
export type WSMessageType =
  | 'audio_chunk'
  | 'transcript_segment'
  | 'followup_prompt'
  | 'number_extracted'
  | 'number_flag'
  | 'credibility_update'
  | 'request_followup'
  | 'error';

export interface WSMessage {
  type: WSMessageType;
  data: unknown;
}
