import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { listingApi } from '@/services/listings'
import { formatCurrency, formatRelative } from '@/utils/format'

export function ListingApplicationsPage() {
  const { slug } = useParams<{ slug: string }>()
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['applications', slug],
    queryFn: () => listingApi.applicationsFor(slug!),
    enabled: Boolean(slug),
  })

  const respond = useMutation({
    mutationFn: ({ id, action }: { id: number; action: 'accept' | 'reject' }) =>
      listingApi.respondToApplication(id, action),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ['applications', slug] }),
  })

  if (isLoading) return <LoadingState />
  if (isError || !data) return <ErrorState message="Could not load applications." />

  const applications = Array.isArray(data) ? data : data.results ?? []

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Applications</h1>
        <p className="mt-1 text-sm text-gray-500">
          Review students who want to use your service.
        </p>
      </div>

      {applications.length === 0 ? (
        <EmptyState
          title="No applications yet"
          description="When students apply to this listing they will show up here."
          action={<Link to="/listings/mine">Back to my services</Link>}
        />
      ) : (
        <ul className="space-y-3">
          {applications.map((application) => (
            <li
              key={application.id}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <Link
                    to={`/profile/${application.applicant.username}`}
                    className="font-medium text-gray-900 hover:text-primary-600"
                  >
                    {application.applicant.display_name}
                  </Link>
                  <p className="mt-0.5 text-sm text-gray-500">
                    Applied {formatRelative(application.created_at)}
                  </p>
                </div>
                <Badge color={statusColor(application.status)}>{application.status}</Badge>
              </div>

              {application.message && (
                <p className="mt-2 rounded-md bg-gray-50 p-3 text-sm text-gray-600">
                  {application.message}
                </p>
              )}
              {application.proposed_price && (
                <p className="mt-2 text-sm text-gray-600">
                  Proposed price:{' '}
                  <span className="font-medium">
                    {formatCurrency(application.proposed_price)}
                  </span>
                </p>
              )}

              {application.status === 'pending' && (
                <div className="mt-3 flex gap-2">
                  <Button
                    size="sm"
                    loading={respond.isPending}
                    onClick={() =>
                      respond.mutate({ id: application.id, action: 'accept' })
                    }
                  >
                    Accept
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      respond.mutate({ id: application.id, action: 'reject' })
                    }
                  >
                    Reject
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