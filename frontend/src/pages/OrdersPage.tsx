import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { Pagination } from '@/components/common/Pagination'
import { orderApi, ORDER_STATUS_LABELS } from '@/services/orders'
import { Avatar } from '@/components/common/Avatar'
import { formatCurrency, formatRelative } from '@/utils/format'

export function OrdersPage() {
  const [role, setRole] = useState<'buyer' | 'provider' | ''>('')
  const [page, setPage] = useState(1)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['orders', { role, page }],
    queryFn: () => orderApi.list(role || undefined, page),
  })

  const orders = data?.results ?? []
  const totalPages = data ? Math.max(1, Math.ceil(data.count / 20)) : 1

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Orders</h1>
          <p className="mt-1 text-sm text-gray-500">
            Services you&rsquo;ve bought and sold.
          </p>
        </div>
        <div className="flex gap-2">
          {(['', 'buyer', 'provider'] as const).map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => {
                setRole(value)
                setPage(1)
              }}
              className={
                role === value
                  ? 'rounded-md bg-primary-600 px-3 py-1.5 text-sm font-medium text-white'
                  : 'rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700'
              }
            >
              {value === '' ? 'All' : value === 'buyer' ? 'As buyer' : 'As seller'}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState message="Could not load orders." />
      ) : orders.length === 0 ? (
        <EmptyState
          title="No orders yet"
          description={
            role === 'provider'
              ? 'When students order your services they will appear here.'
              : 'When you order a service it will appear here.'
          }
          action={
            role === 'provider' ? (
              <Link to="/listings/new">Publish a service</Link>
            ) : (
              <Link to="/marketplace">Browse services</Link>
            )
          }
        />
      ) : (
        <>
          <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
            {orders.map((order) => {
              const other =
                role === 'buyer' ? order.provider : role === 'provider' ? order.buyer : null
              return (
                <li key={order.id}>
                  <Link
                    to={`/orders/${order.id}`}
                    className="flex items-center justify-between gap-4 p-4 hover:bg-gray-50"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900">
                          {order.listing?.title ?? `Order #${order.id}`}
                        </p>
                        <Badge color={statusColor(order.status)}>
                          {ORDER_STATUS_LABELS[order.status]}
                        </Badge>
                      </div>
                      <p className="mt-0.5 text-sm text-gray-500">
                        Placed {formatRelative(order.created_at)}
                        {other && (
                          <>
                            {' · '}
                            <span className="inline-flex items-center gap-1">
                              <Avatar src={other.avatar} name={other.display_name} size="sm" />
                              {other.display_name}
                            </span>
                          </>
                        )}
                      </p>
                    </div>
                    <span className="shrink-0 text-base font-semibold text-gray-900">
                      {formatCurrency(order.price, order.currency)}
                    </span>
                  </Link>
                </li>
              )
            })}
          </ul>
          <Pagination page={page} totalPages={totalPages} onChange={setPage} />
        </>
      )}
    </div>
  )
}