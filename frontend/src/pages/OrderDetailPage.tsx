import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { getErrorMessage } from '@/api/client'
import { Avatar } from '@/components/common/Avatar'
import { Button } from '@/components/common/Button'
import {
  Alert,
  Badge,
  ErrorState,
  LoadingState,
  statusColor,
} from '@/components/common/Feedback'
import { RatingInput } from '@/components/common/Stars'
import { useAuth } from '@/hooks/useAuth'
import { orderApi, ORDER_STATUS_LABELS, type OrderAction } from '@/services/orders'
import { reviewApi } from '@/services/reviews'
import { formatCurrency, formatDate } from '@/utils/format'

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [actionError, setActionError] = useState<string | null>(null)
  const [rating, setRating] = useState(5)
  const [review, setReview] = useState('')

  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['order', id],
    queryFn: () => orderApi.get(Number(id)),
    enabled: Boolean(id),
  })

  const transition = useMutation({
    mutationFn: ({ action }: { action: OrderAction }) => orderApi.transition(order!.id, action),
    onSuccess: () => {
      setActionError(null)
      void queryClient.invalidateQueries({ queryKey: ['order', id] })
    },
    onError: (error) => setActionError(getErrorMessage(error)),
  })

  const payMutation = useMutation({
    mutationFn: orderApi.checkout,
    onSuccess: async (session) => {
      setActionError(null)
      if (session.mode === 'simulation') {
        try {
          await orderApi.mockConfirm(order!.id)
          void queryClient.invalidateQueries({ queryKey: ['order', id] })
        } catch (error) {
          setActionError(getErrorMessage(error))
        }
      } else if (session.url) {
        window.location.href = session.url
      }
    },
    onError: (error) => setActionError(getErrorMessage(error)),
  })

  const submitReview = useMutation({
    mutationFn: () => reviewApi.create(order!.id, rating, review),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['order', id] })
      void queryClient.invalidateQueries({ queryKey: ['reviews'] })
      setReview('')
    },
    onError: (error) => setActionError(getErrorMessage(error)),
  })

  if (isLoading) return <LoadingState />
  if (isError || !order) return <ErrorState message="Order not found." />

  const isBuyer = user?.username === order.buyer.username
  const isProvider = user?.username === order.provider.username

  const actions: { action: OrderAction; label: string; show: boolean }[] = [
    {
      action: 'cancel',
      label: 'Cancel order',
      show: order.status === 'pending_payment' && (isBuyer || isProvider),
    },
    {
      action: 'start',
      label: 'Start work',
      show: order.status === 'paid' && isProvider,
    },
    {
      action: 'complete',
      label: 'Mark delivered',
      show: order.status === 'in_progress' && isProvider,
    },
  ]

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            to="/orders"
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            ← Back to orders
          </Link>
          <h1 className="mt-1 text-2xl font-semibold text-gray-900">
            {order.listing?.title ?? `Order #${order.id}`}
          </h1>
        </div>
        <Badge color={statusColor(order.status)}>
          {ORDER_STATUS_LABELS[order.status]}
        </Badge>
      </div>

      {actionError && (
        <div className="mb-4">
          <Alert variant="error">{actionError}</Alert>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4">
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-900">Details</h2>
            <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-gray-500">Price</dt>
                <dd className="font-medium text-gray-900">
                  {formatCurrency(order.price, order.currency)}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Created</dt>
                <dd className="text-gray-900">{formatDate(order.created_at)}</dd>
              </div>
              {order.paid_at && (
                <div>
                  <dt className="text-gray-500">Paid at</dt>
                  <dd className="text-gray-900">{formatDate(order.paid_at)}</dd>
                </div>
              )}
              {order.completed_at && (
                <div>
                  <dt className="text-gray-500">Completed</dt>
                  <dd className="text-gray-900">{formatDate(order.completed_at)}</dd>
                </div>
              )}
            </dl>
            {order.note && (
              <div className="mt-4 rounded-md bg-gray-50 p-3 text-sm text-gray-600">
                <span className="font-medium text-gray-700">Requirements: </span>
                {order.note}
              </div>
            )}
          </div>

          {/* Parties */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-medium uppercase text-gray-500">Buyer</p>
              <Link
                to={`/profile/${order.buyer.username}`}
                className="mt-2 flex items-center gap-2"
              >
                <Avatar src={order.buyer.avatar} name={order.buyer.display_name} />
                <span className="font-medium text-gray-900">{order.buyer.display_name}</span>
              </Link>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <p className="text-xs font-medium uppercase text-gray-500">Seller</p>
              <Link
                to={`/profile/${order.provider.username}`}
                className="mt-2 flex items-center gap-2"
              >
                <Avatar src={order.provider.avatar} name={order.provider.display_name} />
                <span className="font-medium text-gray-900">{order.provider.display_name}</span>
              </Link>
            </div>
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-sm font-semibold text-gray-900">Actions</h2>

            {order.status === 'pending_payment' && isBuyer && (
              <Button
                className="mt-3 w-full"
                loading={payMutation.isPending}
                onClick={() => payMutation.mutate(order!.id)}
              >
                Pay now
              </Button>
            )}

            {actions
              .filter((a) => a.show)
              .map((a) => (
                <Button
                  key={a.action}
                  variant="outline"
                  className="mt-3 w-full"
                  loading={transition.isPending}
                  onClick={() => transition.mutate({ action: a.action })}
                >
                  {a.label}
                </Button>
              ))}

            {/* Review box */}
            {order.status === 'completed' && isBuyer && (
              <div className="mt-5 border-t border-gray-100 pt-4">
                <p className="text-sm font-medium text-gray-700">Leave a review</p>
                <div className="mt-2">
                  <RatingInput value={rating} onChange={setRating} />
                </div>
                <textarea
                  rows={3}
                  value={review}
                  onChange={(e) => setReview(e.target.value)}
                  placeholder="How was your experience?"
                  className="mt-2 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <Button
                  size="sm"
                  className="mt-2 w-full"
                  loading={submitReview.isPending}
                  onClick={() => submitReview.mutate()}
                >
                  Submit review
                </Button>
              </div>
            )}

            <Link
              to="/messages"
              state={{ orderId: order.id }}
              className="mt-4 block text-center text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              View conversation
            </Link>
          </div>
        </aside>
      </div>
    </div>
  )
}