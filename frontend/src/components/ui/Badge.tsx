interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md';
}

const variants = {
  default: 'bg-gray-100 text-gray-700',
  success: 'bg-green-100 text-green-700',
  warning: 'bg-yellow-100 text-yellow-700',
  danger: 'bg-red-100 text-red-700',
  info: 'bg-blue-100 text-blue-700',
};

export default function Badge({ children, variant = 'default', size = 'sm' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center font-medium rounded-full ${variants[variant]} ${
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
      }`}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; variant: BadgeProps['variant'] }> = {
    draft: { label: '草稿', variant: 'default' },
    scheduled: { label: '已排期', variant: 'info' },
    live: { label: '进行中', variant: 'warning' },
    completed: { label: '已完成', variant: 'success' },
    pending: { label: '等待中', variant: 'default' },
    running: { label: '运行中', variant: 'warning' },
    failed: { label: '失败', variant: 'danger' },
    unverified: { label: '待验证', variant: 'default' },
    consistent: { label: '一致', variant: 'success' },
    flagged: { label: '异常', variant: 'danger' },
  };

  const { label, variant } = config[status] || { label: status, variant: 'default' as const };
  return <Badge variant={variant}>{label}</Badge>;
}
