import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { Button } from '@/components/common/Button'
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { reportApi } from '@/services/reports'
import { titleCase, formatRelative } from '@/utils/format'

export function ReportsPage({ admin = false }: { admin?: boolean }) {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [notes, setNotes] = useState<Record<number, string>>({})

  const { data, isLoading, isError } = useQuery({
    queryKey: ['reports', { admin, statusFilter }],
    queryFn: () => reportApi.list(admin ? { status: statusFilter } : undefined),
  })

  const review = useMutation({
    mutationFn: ({ id, action }: { id: number; action: 'resolve' | 'reject' }) =>
      reportApi.review(id, action, notes[id] ?? ''),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ['reports'] }),
  })

  if (isLoading) return <LoadingState />
  if (isError || !data) return <ErrorState message="Could not load reports." />

  const reports = data.results

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            {admin ? 'Moderation queue' : 'My reports'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            {admin
              ? 'Review reports submitted by the community.'
              : 'Reports you have submitted about content or users.'}
          </p>
        </div>
        {admin && (
          <div className="flex flex-wrap gap-2">
            {['', 'pending', 'reviewing', 'resolved', 'rejected'].map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setStatusFilter(value)}
                className={
                  statusFilter === value
                    ? 'rounded-md bg-primary-600 px-3 py-1.5 text-sm font-medium text-white'
                    : 'rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700'
                }
              >
                {value === '' ? 'All' : titleCase(value)}
              </button>
            ))}
          </div>
        )}
      </div>

      {reports.length === 0 ? (
        <EmptyState
          title="No reports"
          description={
            admin
              ? 'There are no reports matching this filter.'
              : 'If something looks wrong you can report it and track it here.'
          }
        />
      ) : (
        <ul className="space-y-4">
          {reports.map((report) => (
            <li
              key={report.id}
              className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {titleCase(report.target_type)} #{report.target_id}
                    {report.target_name && (
                      <span className="ml-2 font-normal text-gray-500">
                        {report.target_name}
                      </span>
                    )}
                  </p>
                  <p className="mt-0.5 text-sm text-gray-600">
                    <span className="font-medium">{report.reason}</span>
                    {report.description && ` — ${report.description}`}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    Reported {formatRelative(report.created_at)} by{' '}
                    {report.reporter.username}
                  </p>
                </div>
                <Badge color={statusColor(report.status)}>{report.status}</Badge>
              </div>

              {report.admin_notes && (
                <p className="mt-2 rounded-md bg-gray-50 p-3 text-sm text-gray-600">
                  <span className="font-medium text-gray-700">Admin notes: </span>
                  {report.admin_notes}
                </p>
              )}

              {admin && report.status === 'pending' && (
                <div className="mt-3 space-y-2">
                  <input
                    type="text"
                    value={notes[report.id] ?? ''}
                    onChange={(e) =>
                      setNotes((prev) => ({ ...prev, [report.id]: e.target.value }))
                    }
                    placeholder="Admin notes (optional)"
                    className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      loading={review.isPending}
                      onClick={() => review.mutate({ id: report.id, action: 'resolve' })}
                    >
                      Resolve
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => review.mutate({ id: report.id, action: 'reject' })}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}