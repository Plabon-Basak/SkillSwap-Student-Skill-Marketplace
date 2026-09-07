import { useQuery } from '@tanstack/react-query'
import { Link, useLocation } from 'react-router-dom'

import { Avatar } from '@/components/common/Avatar'
import { Badge, EmptyState, LoadingState } from '@/components/common/Feedback'
import { messagingApi } from '@/services/messaging'
import { formatRelative } from '@/utils/format'

export function MessagesPage() {
  const location = useLocation()
  const orderId = (location.state as { orderId?: number } | null)?.orderId

  const { data: threads, isLoading } = useQuery({
    queryKey: ['threads'],
    queryFn: messagingApi.threads,
  })

  const visible = orderId ? threads?.filter((t) => t.order === orderId) : threads

  if (isLoading) return <LoadingState />

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Messages</h1>
        <p className="mt-1 text-sm text-gray-500">
          Conversations with buyers and sellers about orders.
        </p>
      </div>

      {!visible || visible.length === 0 ? (
        <EmptyState
          title="No conversations yet"
          description="When you place or receive an order, its conversation thread appears here."
          action={<Link to="/marketplace">Browse services</Link>}
        />
      ) : (
        <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
          {visible.map((thread) => {
            return (
              <li key={thread.id}>
                <Link
                  to={`/messages/${thread.id}`}
                  className="flex items-center justify-between gap-4 p-4 hover:bg-gray-50"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <Avatar
                      src={thread.buyer.avatar}
                      name={thread.buyer.display_name}
                    />
                    <div className="min-w-0">
                      <p className="truncate font-medium text-gray-900">
                        {thread.buyer.display_name} × {thread.provider.display_name}
                      </p>
                      <p className="truncate text-sm text-gray-500">
                        Order #{thread.order}
                        {thread.last_message_at &&
                          ` · last message ${formatRelative(thread.last_message_at)}`}
                      </p>
                    </div>
                  </div>
                  {thread.unread_count > 0 && (
                    <Badge color="red">{thread.unread_count} unread</Badge>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}