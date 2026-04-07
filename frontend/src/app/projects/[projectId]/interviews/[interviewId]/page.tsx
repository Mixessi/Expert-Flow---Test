'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  getInterview,
  startResearch,
  getResearch,
  uploadDocument,
  listDocuments,
  deleteDocument,
  generateOutline,
  getOutline,
} from '@/lib/api';
import type { Interview, ResearchResult, ReferenceDocument, Outline } from '@/lib/types';
import Header from '@/components/layout/Header';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/Badge';
import Badge from '@/components/ui/Badge';

export default function InterviewDetailPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const interviewId = params.interviewId as string;

  const [interview, setInterview] = useState<Interview | null>(null);
  const [research, setResearch] = useState<ResearchResult[]>([]);
  const [documents, setDocuments] = useState<ReferenceDocument[]>([]);
  const [outline, setOutline] = useState<Outline | null>(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [outlineLoading, setOutlineLoading] = useState(false);
  const [uploadingDoc, setUploadingDoc] = useState(false);

  const load = useCallback(async () => {
    const [iv, res, docs] = await Promise.all([
      getInterview(interviewId),
      getResearch(interviewId).catch(() => []),
      listDocuments(interviewId).catch(() => []),
    ]);
    setInterview(iv);
    setResearch(res);
    setDocuments(docs);
    try {
      const ol = await getOutline(interviewId);
      setOutline(ol);
    } catch {
      setOutline(null);
    }
  }, [interviewId]);

  useEffect(() => { load(); }, [load]);

  const handleResearch = async () => {
    if (!interview?.core_questions) return;
    setResearchLoading(true);
    try {
      await startResearch(interviewId, interview.core_questions);
      await load();
    } catch (error) {
      console.error(error);
    } finally {
      setResearchLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingDoc(true);
    try {
      await uploadDocument(interviewId, file);
      await load();
    } catch (error) {
      console.error(error);
    } finally {
      setUploadingDoc(false);
      e.target.value = '';
    }
  };

  const handleDeleteDoc = async (docId: string) => {
    await deleteDocument(docId);
    await load();
  };

  const handleGenerateOutline = async () => {
    setOutlineLoading(true);
    try {
      const ol = await generateOutline(interviewId);
      setOutline(ol);
    } catch (error) {
      console.error(error);
    } finally {
      setOutlineLoading(false);
    }
  };

  if (!interview) return <div className="p-6 text-gray-400">加载中...</div>;

  return (
    <div>
      <Header
        title={interview.expert_name || '访谈准备'}
        subtitle={`${interview.expert_company || ''} ${interview.expert_title || ''}`.trim() || '专家访谈'}
        actions={
          <div className="flex gap-3">
            <StatusBadge status={interview.status} />
            {interview.status === 'draft' && outline && (
              <Link href={`/projects/${projectId}/interviews/${interviewId}/live`}>
                <Button>进入访谈</Button>
              </Link>
            )}
            {interview.status === 'completed' && (
              <Link href={`/projects/${projectId}/interviews/${interviewId}/notes`}>
                <Button>查看纪要</Button>
              </Link>
            )}
          </div>
        }
      />

      <div className="p-6 space-y-6">
        {/* Core Questions */}
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-gray-900">核心研究问题</h3>
          </CardHeader>
          <CardBody>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{interview.core_questions || '未设置核心问题'}</p>
          </CardBody>
        </Card>

        {/* Step 1: AI Research */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Step 1: AI 智能调研</h3>
            <Button onClick={handleResearch} loading={researchLoading} size="sm">
              {research.length > 0 ? '重新调研' : '开始调研'}
            </Button>
          </CardHeader>
          <CardBody>
            {research.length === 0 ? (
              <p className="text-sm text-gray-400">点击"开始调研"，AI将基于核心问题自动搜索公开信息</p>
            ) : (
              research.map((r) => (
                <div key={r.id} className="space-y-4">
                  <div className="flex items-center gap-2 mb-3">
                    <StatusBadge status={r.status} />
                    <span className="text-xs text-gray-400">查询: {r.query}</span>
                  </div>
                  {r.company_overview && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">公司概览</h4>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap">{r.company_overview}</p>
                    </div>
                  )}
                  {r.industry_data && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">行业数据</h4>
                      <p className="text-sm text-gray-600 whitespace-pre-wrap">{r.industry_data}</p>
                    </div>
                  )}
                  {r.key_numbers && r.key_numbers.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">关键数字</h4>
                      <div className="overflow-x-auto">
                        <table className="text-sm w-full">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-3 py-2 text-left">指标</th>
                              <th className="px-3 py-2 text-left">数值</th>
                              <th className="px-3 py-2 text-left">来源</th>
                              <th className="px-3 py-2 text-left">日期</th>
                            </tr>
                          </thead>
                          <tbody>
                            {r.key_numbers.map((num, i) => (
                              <tr key={i} className="border-t">
                                <td className="px-3 py-2">{num.metric}</td>
                                <td className="px-3 py-2 font-medium">{num.value}</td>
                                <td className="px-3 py-2 text-gray-500">{num.source}</td>
                                <td className="px-3 py-2 text-gray-500">{num.date}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                  {r.info_gaps && r.info_gaps.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">信息空白点（访谈聚焦方向）</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {r.info_gaps.map((gap, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-red-500 mt-0.5">!</span>
                            <span>{gap}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))
            )}
          </CardBody>
        </Card>

        {/* Step 2: Reference Documents */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Step 2: 参考文档</h3>
            <label className="cursor-pointer">
              <span className={`inline-flex items-center justify-center font-medium rounded-lg transition-colors px-3 py-1.5 text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300 ${uploadingDoc ? 'opacity-50 pointer-events-none' : ''}`}>
                {uploadingDoc ? '上传中...' : '上传文档'}
              </span>
              <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.doc,.txt,.md,.csv" />
            </label>
          </CardHeader>
          <CardBody>
            {documents.length === 0 ? (
              <p className="text-sm text-gray-400">上传参考文档，用于提纲生成和访谈中数据校验</p>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">
                        {doc.filename.endsWith('.pdf') ? '📄' : doc.filename.endsWith('.docx') ? '📝' : '📃'}
                      </span>
                      <div>
                        <p className="text-sm font-medium text-gray-700">{doc.filename}</p>
                        <p className="text-xs text-gray-400">{(doc.file_size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteDoc(doc.id)}
                      className="text-sm text-red-500 hover:text-red-700"
                    >
                      删除
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Step 3: Interview Outline */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Step 3: 智能提纲生成</h3>
            <Button onClick={handleGenerateOutline} loading={outlineLoading} size="sm">
              {outline ? '重新生成' : '生成提纲'}
            </Button>
          </CardHeader>
          <CardBody>
            {!outline ? (
              <p className="text-sm text-gray-400">基于调研结果和参考文档，AI将生成结构化的访谈提纲</p>
            ) : (
              <div className="space-y-4">
                {outline.content.sections?.map((section, si) => (
                  <div key={si} className="border rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-1">{section.title}</h4>
                    <p className="text-xs text-gray-500 mb-3">{section.purpose}</p>
                    <div className="space-y-2">
                      {section.questions?.map((q, qi) => (
                        <div key={qi} className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                          <Badge
                            variant={q.priority === 'high' ? 'danger' : q.priority === 'medium' ? 'warning' : 'default'}
                            size="sm"
                          >
                            {q.type === 'test_question' ? 'TQ' : q.priority === 'high' ? '高' : q.priority === 'medium' ? '中' : '低'}
                          </Badge>
                          <div className="flex-1">
                            <p className="text-sm text-gray-800">{q.text}</p>
                            <p className="text-xs text-gray-400 mt-0.5">{q.rationale}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )) || (
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {outline.content.raw_text || JSON.stringify(outline.content, null, 2)}
                  </p>
                )}
                {outline.content.key_hypotheses && outline.content.key_hypotheses.length > 0 && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-700 mb-2">核心假设</h4>
                    <ul className="text-sm text-blue-600 space-y-1">
                      {outline.content.key_hypotheses.map((h, i) => (
                        <li key={i}>- {h}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
