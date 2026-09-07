import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { adminApi } from '@/services/reports'
import type { Listing } from '@/types'
import { formatCurrency, formatRelative, titleCase } from '@/utils/format'

const STATUS_FILTERS = ['published', 'pending', 'rejected', 'suspended', 'archived']

function listingStatusLabel(status: string): string {
  return titleCase(status)
}

export function AdminDashboard() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('pending')

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'listings', statusFilter],
    queryFn: () => adminApi.listings(statusFilter),
  })

  const moderate = useMutation({
    mutationFn: ({
      id,
      action,
    }: {
      id: number
      action: 'approve' | 'reject' | 'suspend' | 'remove'
    }) => adminApi.moderateListing(id, action),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin', 'listings'] })
    },
  })

  if (isLoading) return <LoadingState />
  if (isError || !data) return <ErrorState message="Could not load listings." />

  const raw = Array.isArray(data) ? data : data.results
  const listings: Listing[] = raw
  const pendingCount = listings.filter((l) => l.moderation_status === 'pending').length

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Admin dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Moderate listings and keep the marketplace safe.
        </p>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-3xl font-bold text-gray-900">{pendingCount}</p>
          <p className="text-sm text-gray-500">Pending review</p>
        </div>
        <Link
          to="/admin/reports"
          className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:border-primary-300"
        >
          <p className="text-sm font-medium text-primary-600">Moderation queue</p>
          <p className="mt-1 text-sm text-gray-500">
            Review community reports → (resolved, rejected…)
          </p>
        </Link>
      </div>

      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((value) => (
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
            {listingStatusLabel(value)}
          </button>
        ))}
      </div>

      {listings.length === 0 ? (
        <div className="mt-4">
          <EmptyState
            title="Nothing in this view"
            description="No listings match this status filter."
          />
        </div>
      ) : (
        <ul className="mt-4 divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
          {listings.map((listing) => (
            <li key={listing.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="font-medium text-gray-900">{listing.title}</p>
                  <p className="mt-0.5 text-sm text-gray-500">
                    {listing.provider.display_name} · {formatCurrency(listing.price, listing.currency)} ·{' '}
                    {formatRelative(listing.created_at)}
                  </p>
                </div>
                <Badge color={statusColor(listing.moderation_status)}>
                  {listing.moderation_status ?? 'unknown'}
                </Badge>
              </div>

              {listing.moderation_status === 'pending' && (
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    loading={moderate.isPending}
                    onClick={() => moderate.mutate({ id: listing.id, action: 'approve' })}
                  >
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => moderate.mutate({ id: listing.id, action: 'reject' })}
                  >
                    Reject
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => moderate.mutate({ id: listing.id, action: 'suspend' })}
                  >
                    Suspend
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => moderate.mutate({ id: listing.id, action: 'remove' })}
                  >
                    Remove
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}