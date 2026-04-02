'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getProject, listInterviews } from '@/lib/api';
import type { Project, Interview } from '@/lib/types';
import Header from '@/components/layout/Header';
import Card, { CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/Badge';

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [project, setProject] = useState<Project | null>(null);
  const [interviews, setInterviews] = useState<Interview[]>([]);

  useEffect(() => {
    getProject(projectId).then(setProject).catch(console.error);
    listInterviews(projectId).then(setInterviews).catch(console.error);
  }, [projectId]);

  if (!project) return <div className="p-6 text-gray-400">加载中...</div>;

  return (
    <div>
      <Header
        title={project.name}
        subtitle={project.description || undefined}
        actions={
          <Link href={`/projects/${projectId}/interviews/new`}>
            <Button>+ 新建访谈</Button>
          </Link>
        }
      />
      <div className="p-6">
        {/* Project info */}
        <Card className="mb-6">
          <CardBody>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">行业：</span>
                <span className="text-gray-900">{project.industry || '未指定'}</span>
              </div>
              <div>
                <span className="text-gray-500">研究目标：</span>
                <span className="text-gray-900">{project.research_goals || '未指定'}</span>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Interview list */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">访谈列表</h3>
        {interviews.length === 0 ? (
          <Card>
            <CardBody className="text-center py-12">
              <p className="text-gray-500 mb-4">还没有访谈</p>
              <Link href={`/projects/${projectId}/interviews/new`}>
                <Button>+ 新建访谈</Button>
              </Link>
            </CardBody>
          </Card>
        ) : (
          <div className="space-y-3">
            {interviews.map((interview) => (
              <Link
                key={interview.id}
                href={`/projects/${projectId}/interviews/${interview.id}`}
              >
                <Card hover className="mb-3">
                  <CardBody className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <h4 className="font-semibold text-gray-900">
                          {interview.expert_name || '待定专家'}
                        </h4>
                        <StatusBadge status={interview.status} />
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                        {interview.expert_company && <span>{interview.expert_company}</span>}
                        {interview.expert_title && <span>{interview.expert_title}</span>}
                      </div>
                      {interview.core_questions && (
                        <p className="text-sm text-gray-400 mt-1 line-clamp-1">{interview.core_questions}</p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(interview.created_at).toLocaleDateString('zh-CN')}
                    </span>
                  </CardBody>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
