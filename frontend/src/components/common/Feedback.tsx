import type { ReactNode } from 'react'

import { classNames } from '@/utils/format'

interface CardProps {
  children: ReactNode
  className?: string
  padding?: boolean
}

export function Card({ children, className, padding = true }: CardProps) {
  return (
    <div
      className={classNames(
        'rounded-lg border border-gray-200 bg-white shadow-sm',
        padding && 'p-5',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string
  subtitle?: string
  actions?: ReactNode
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}

export function Alert({
  variant = 'info',
  children,
}: {
  variant?: 'info' | 'success' | 'warning' | 'error'
  children: ReactNode
}) {
  const styles = {
    info: 'border-blue-200 bg-blue-50 text-blue-800',
    success: 'border-green-200 bg-green-50 text-green-800',
    warning: 'border-amber-200 bg-amber-50 text-amber-800',
    error: 'border-red-200 bg-red-50 text-red-800',
  }
  return (
    <div role="alert" className={classNames('rounded-md border px-4 py-3 text-sm', styles[variant])}>
      {children}
    </div>
  )
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={classNames(
        'inline-block h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-primary-600',
        className,
      )}
      role="status"
      aria-label="Loading"
    />
  )
}

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-500">
      <Spinner className="h-8 w-8" />
      <p className="text-sm">{label}</p>
    </div>
  )
}

export function ErrorState({
  message = 'Something went wrong.',
  onRetry,
}: {
  message?: string
  onRetry?: () => void
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-6 text-center">
      <p className="text-sm text-red-700">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 text-sm font-medium text-red-700 underline hover:text-red-800"
        >
          Try again
        </button>
      )}
    </div>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-white px-6 py-14 text-center">
      <h3 className="text-base font-medium text-gray-900">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-gray-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function Badge({
  children,
  color = 'gray',
}: {
  children: ReactNode
  color?: 'gray' | 'green' | 'amber' | 'red' | 'blue' | 'purple'
}) {
  const colors = {
    gray: 'bg-gray-100 text-gray-700',
    green: 'bg-green-100 text-green-800',
    amber: 'bg-amber-100 text-amber-800',
    red: 'bg-red-100 text-red-800',
    blue: 'bg-blue-100 text-blue-800',
    purple: 'bg-purple-100 text-purple-800',
  }
  return (
    <span
      className={classNames(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        colors[color],
      )}
    >
      {children}
    </span>
  )
}

export const statusColor = (
  status: string,
): 'gray' | 'green' | 'amber' | 'red' | 'blue' | 'purple' => {
  const positives = ['completed', 'published', 'accepted', 'resolved', 'active', 'paid']
  const warnings = ['pending', 'in_progress', 'reviewing', 'pending_payment']
  const negatives = ['cancelled', 'rejected', 'suspended', 'refunded', 'withdrawn', 'removed']
  if (positives.includes(status)) return 'green'
  if (negatives.includes(status)) return 'red'
  if (warnings.includes(status)) return 'amber'
  return 'blue'
}