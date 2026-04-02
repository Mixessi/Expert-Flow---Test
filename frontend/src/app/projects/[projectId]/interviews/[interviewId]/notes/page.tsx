'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getInterview, getNotes, generateNotes, getNumbers } from '@/lib/api';
import type { Interview, Note, NumberRecord } from '@/lib/types';
import Header from '@/components/layout/Header';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/Badge';

export default function NotesPage() {
  const params = useParams();
  const interviewId = params.interviewId as string;

  const [interview, setInterview] = useState<Interview | null>(null);
  const [note, setNote] = useState<Note | null>(null);
  const [numbers, setNumbers] = useState<NumberRecord[]>([]);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    getInterview(interviewId).then(setInterview).catch(console.error);
    getNotes(interviewId).then(setNote).catch(() => setNote(null));
    getNumbers(interviewId).then(setNumbers).catch(() => setNumbers([]));
  }, [interviewId]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const n = await generateNotes(interviewId);
      setNote(n);
    } catch (error) {
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div>
      <Header
        title="访谈纪要"
        subtitle={interview ? `${interview.expert_name || '专家'} - ${interview.expert_company || ''}` : ''}
        actions={
          <Button onClick={handleGenerate} loading={generating}>
            {note ? '重新生成纪要' : '生成纪要'}
          </Button>
        }
      />
      <div className="p-6 space-y-6 max-w-4xl">
        {!note ? (
          <Card>
            <CardBody className="text-center py-12">
              <p className="text-gray-500 mb-4">尚未生成访谈纪要</p>
              <Button onClick={handleGenerate} loading={generating}>生成 AI 纪要</Button>
            </CardBody>
          </Card>
        ) : (
          <>
            {/* Summary */}
            {note.summary && (
              <Card>
                <CardHeader>
                  <h3 className="font-semibold text-gray-900">核心发现摘要</h3>
                </CardHeader>
                <CardBody>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{note.summary}</p>
                </CardBody>
              </Card>
            )}

            {/* Key Numbers Table */}
            <Card>
              <CardHeader>
                <h3 className="font-semibold text-gray-900">
                  关键数字汇总 ({note.key_numbers?.length || numbers.length} 项)
                </h3>
              </CardHeader>
              <CardBody>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">数字</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">上下文</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">分类</th>
                        <th className="px-3 py-2 text-left font-medium text-gray-600">验证状态</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(note.key_numbers || []).map((num, i) => (
                        <tr key={i} className="border-t hover:bg-gray-50">
                          <td className="px-3 py-2 font-bold text-gray-900">{num.value}</td>
                          <td className="px-3 py-2 text-gray-600 max-w-xs truncate">{num.context}</td>
                          <td className="px-3 py-2">
                            {num.category && (
                              <span className="bg-gray-100 text-gray-600 text-xs rounded px-2 py-0.5">
                                {num.category}
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <StatusBadge status={num.verification} />
                          </td>
                        </tr>
                      ))}
                      {(!note.key_numbers || note.key_numbers.length === 0) && numbers.map((num) => (
                        <tr key={num.id} className="border-t hover:bg-gray-50">
                          <td className="px-3 py-2 font-bold text-gray-900">{num.value}</td>
                          <td className="px-3 py-2 text-gray-600 max-w-xs truncate">{num.context}</td>
                          <td className="px-3 py-2">
                            {num.category && (
                              <span className="bg-gray-100 text-gray-600 text-xs rounded px-2 py-0.5">
                                {num.category}
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            <StatusBadge status={num.verification} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>

            {/* Full Notes */}
            {note.full_notes && (
              <Card>
                <CardHeader>
                  <h3 className="font-semibold text-gray-900">完整纪要</h3>
                </CardHeader>
                <CardBody>
                  <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                    {note.full_notes}
                  </div>
                </CardBody>
              </Card>
            )}

            {/* Action Items */}
            {note.action_items && note.action_items.length > 0 && (
              <Card>
                <CardHeader>
                  <h3 className="font-semibold text-gray-900">行动建议</h3>
                </CardHeader>
                <CardBody>
                  <ul className="space-y-2">
                    {note.action_items.map((item, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-blue-500 mt-0.5">-</span>
                        <span className="text-gray-700">{item.item}</span>
                      </li>
                    ))}
                  </ul>
                </CardBody>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}
