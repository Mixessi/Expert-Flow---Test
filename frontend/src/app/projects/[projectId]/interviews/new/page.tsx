'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { createInterview } from '@/lib/api';
import Header from '@/components/layout/Header';
import Card, { CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';

export default function NewInterviewPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.projectId as string;
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    expert_name: '',
    expert_title: '',
    expert_company: '',
    expert_bio: '',
    core_questions: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const interview = await createInterview(projectId, form);
      router.push(`/projects/${projectId}/interviews/${interview.id}`);
    } catch (error) {
      console.error(error);
      alert('创建访谈失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header title="新建访谈" subtitle="填写专家信息和核心研究问题" />
      <div className="p-6 max-w-2xl">
        <Card>
          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">专家姓名</label>
                  <input
                    type="text"
                    value={form.expert_name}
                    onChange={(e) => setForm({ ...form, expert_name: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="专家姓名"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">所在公司</label>
                  <input
                    type="text"
                    value={form.expert_company}
                    onChange={(e) => setForm({ ...form, expert_company: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="公司名称"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">职位/头衔</label>
                <input
                  type="text"
                  value={form.expert_title}
                  onChange={(e) => setForm({ ...form, expert_title: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="例：高级副总裁、行业分析师"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">专家背景</label>
                <textarea
                  value={form.expert_bio}
                  onChange={(e) => setForm({ ...form, expert_bio: e.target.value })}
                  rows={3}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="专家的背景信息、从业经历、擅长领域等"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  核心研究问题 *
                </label>
                <textarea
                  required
                  value={form.core_questions}
                  onChange={(e) => setForm({ ...form, core_questions: e.target.value })}
                  rows={5}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="描述你希望通过此次访谈获取的核心信息。例如：&#10;1. XX公司在XX领域的市场份额和增长策略&#10;2. XX行业的竞争格局变化趋势&#10;3. XX技术的实际应用效果和ROI"
                />
                <p className="text-xs text-gray-400 mt-1">
                  核心问题将用于 AI 调研和提纲生成，请尽可能具体
                </p>
              </div>
              <div className="flex gap-3 pt-2">
                <Button type="submit" loading={loading}>创建访谈</Button>
                <Button type="button" variant="secondary" onClick={() => router.back()}>取消</Button>
              </div>
            </form>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
