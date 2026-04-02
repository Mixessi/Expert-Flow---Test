'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listProjects, deleteProject } from '@/lib/api';
import type { Project } from '@/lib/types';
import Header from '@/components/layout/Header';
import Card, { CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    listProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`确定删除项目「${name}」？此操作不可撤销。`)) return;
    await deleteProject(id);
    load();
  };

  return (
    <div>
      <Header
        title="研究项目"
        subtitle="管理所有研究项目和访谈"
        actions={
          <Link href="/projects/new">
            <Button>+ 新建项目</Button>
          </Link>
        }
      />
      <div className="p-6">
        {loading ? (
          <p className="text-gray-400">加载中...</p>
        ) : projects.length === 0 ? (
          <Card>
            <CardBody className="text-center py-12">
              <p className="text-gray-500 mb-4">还没有项目</p>
              <Link href="/projects/new">
                <Button>+ 新建项目</Button>
              </Link>
            </CardBody>
          </Card>
        ) : (
          <div className="space-y-3">
            {projects.map((project) => (
              <Card key={project.id} hover>
                <CardBody className="flex items-center justify-between">
                  <Link href={`/projects/${project.id}`} className="flex-1">
                    <h4 className="font-semibold text-gray-900">{project.name}</h4>
                    {project.description && (
                      <p className="text-sm text-gray-500 mt-1">{project.description}</p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      {project.industry && <span className="bg-gray-100 px-2 py-0.5 rounded">{project.industry}</span>}
                      <span>创建于 {new Date(project.created_at).toLocaleDateString('zh-CN')}</span>
                    </div>
                  </Link>
                  <Button variant="ghost" size="sm" onClick={() => handleDelete(project.id, project.name)}>
                    删除
                  </Button>
                </CardBody>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
