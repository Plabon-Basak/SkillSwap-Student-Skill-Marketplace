import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import {
  Badge,
  EmptyState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { listingApi } from '@/services/listings'
import { orderApi } from '@/services/orders'
import { formatCurrency, formatRelative } from '@/utils/format'

export function MyApplicationsPage() {
  const queryClient = useQueryClient()
  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications', 'mine'],
    queryFn: listingApi.myApplications,
  })

  const withdraw = useMutation({
    mutationFn: (id: number) => listingApi.respondToApplication(id, 'withdraw'),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ['applications', 'mine'] }),
  })

  const placeOrder = useMutation({
    mutationFn: (applicationId: number) => orderApi.create(applicationId),
    onSuccess: (order) => {
      void queryClient.invalidateQueries({ queryKey: ['orders'] })
      void queryClient.invalidateQueries({ queryKey: ['applications', 'mine'] })
      window.location.href = `/orders/${order.id}`
    },
  })

  if (isLoading) return <LoadingState />

  const list = applications?.results ?? []

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">My applications</h1>
        <p className="mt-1 text-sm text-gray-500">
          Track the services you&rsquo;ve applied to.
        </p>
      </div>

      {list.length === 0 ? (
        <EmptyState
          title="No applications yet"
          description="Browse the marketplace and apply to a service to get started."
          action={<Link to="/marketplace">Browse services</Link>}
        />
      ) : (
        <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
          {list.map((application) => (
            <li
              key={application.id}
              className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <Link
                  to={`/listing/${application.listing.slug}`}
                  className="font-medium text-gray-900 hover:text-primary-600"
                >
                  {application.listing.title}
                </Link>
                <p className="mt-0.5 text-sm text-gray-500">
                  {formatCurrency(application.listing.price)} ·{' '}
                  {formatRelative(application.created_at)}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Badge color={statusColor(application.status)}>
                  {application.status}
                </Badge>
                {application.status === 'accepted' && (
                  <Button
                    size="sm"
                    loading={placeOrder.isPending}
                    onClick={() => placeOrder.mutate(application.id)}
                  >
                    Create order
                  </Button>
                )}
                {application.status === 'pending' && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => withdraw.mutate(application.id)}
                  >
                    Withdraw
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}