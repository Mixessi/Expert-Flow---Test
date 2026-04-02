'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listProjects } from '@/lib/api';
import type { Project } from '@/lib/types';
import Header from '@/components/layout/Header';
import Card, { CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <Header
        title="仪表盘"
        subtitle="ExpertFlow - 专家访谈智能助手"
        actions={
          <Link href="/projects/new">
            <Button>+ 新建项目</Button>
          </Link>
        }
      />
      <div className="p-6">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <Card>
            <CardBody>
              <p className="text-sm text-gray-500">研究项目</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{projects.length}</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <p className="text-sm text-gray-500">进行中访谈</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">0</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <p className="text-sm text-gray-500">已完成访谈</p>
              <p className="text-3xl font-bold text-green-600 mt-1">0</p>
            </CardBody>
          </Card>
        </div>

        {/* Recent Projects */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">最近项目</h3>
        {loading ? (
          <p className="text-gray-400">加载中...</p>
        ) : projects.length === 0 ? (
          <Card>
            <CardBody className="text-center py-12">
              <p className="text-gray-500 mb-4">还没有项目，创建第一个研究项目开始吧</p>
              <Link href="/projects/new">
                <Button>+ 新建项目</Button>
              </Link>
            </CardBody>
          </Card>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {projects.slice(0, 6).map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`}>
                <Card hover>
                  <CardBody>
                    <h4 className="font-semibold text-gray-900">{project.name}</h4>
                    {project.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{project.description}</p>
                    )}
                    <div className="flex items-center gap-3 mt-3 text-xs text-gray-400">
                      {project.industry && <span>{project.industry}</span>}
                      <span>{new Date(project.created_at).toLocaleDateString('zh-CN')}</span>
                    </div>
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
