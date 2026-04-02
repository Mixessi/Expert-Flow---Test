'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createProject } from '@/lib/api';
import Header from '@/components/layout/Header';
import Card, { CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    research_goals: '',
    industry: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const project = await createProject(form);
      router.push(`/projects/${project.id}`);
    } catch (error) {
      console.error(error);
      alert('创建项目失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header title="新建研究项目" subtitle="创建一个新的研究项目来组织你的专家访谈" />
      <div className="p-6 max-w-2xl">
        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">项目名称 *</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="例：XX行业竞争格局研究"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">行业</label>
                <input
                  type="text"
                  value={form.industry}
                  onChange={(e) => setForm({ ...form, industry: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="例：新能源、消费科技、医疗健康"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">项目描述</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={3}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="简要描述研究背景和目标"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">研究目标</label>
                <textarea
                  value={form.research_goals}
                  onChange={(e) => setForm({ ...form, research_goals: e.target.value })}
                  rows={4}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="详细描述你希望通过专家访谈获取的核心信息、关键假设和研究问题"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button type="submit" loading={loading}>创建项目</Button>
                <Button type="button" variant="secondary" onClick={() => router.back()}>取消</Button>
              </div>
            </form>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
