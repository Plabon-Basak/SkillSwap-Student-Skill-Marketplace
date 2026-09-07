import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import { EmptyState, LoadingState } from '@/components/common/Feedback'
import { notificationsApi, type Notification } from '@/services/notifications'
import { formatRelative } from '@/utils/format'

function notificationHref(n: Notification): string | null {
  switch (n.target_type) {
    case 'listing': {
      const slug = n.data?.slug
      return typeof slug === 'string' ? `/listing/${slug}` : null
    }
    case 'application':
    case 'order':
      return n.target_id ? `/orders/${n.target_id}` : null
    case 'message':
    case 'thread':
      return n.target_id ? `/messages/${n.target_id}` : null
    case 'report':
      return null
    default:
      return null
  }
}

export function NotificationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list(),
  })

  const queryClient = useQueryClient()

  const markRead = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const markAllRead = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  })

  if (isLoading) return <LoadingState />

  const notifications = data?.results ?? []

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Notifications</h1>
          <p className="mt-1 text-sm text-gray-500">
            Recent activity on your listings and orders.
          </p>
        </div>
        {notifications.some((n) => !n.is_read) && (
          <Button variant="outline" size="sm" loading={markAllRead.isPending} onClick={() => markAllRead.mutate()}>
            Mark all read
          </Button>
        )}
      </div>

      {notifications.length === 0 ? (
        <EmptyState
          title="No notifications"
          description="Updates about applications, orders, and messages will appear here."
        />
      ) : (
        <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
          {notifications.map((notification) => {
            const href = notificationHref(notification)
            const body = (
              <>
                <p className="font-medium text-gray-900">{notification.verb}</p>
                {notification.data &&
                  typeof notification.data.text === 'string' && (
                    <p className="mt-0.5 text-sm text-gray-500">
                      {String(notification.data.text)}
                    </p>
                  )}
                <p className="mt-0.5 text-xs text-gray-400">
                  {formatRelative(notification.created_at)}
                </p>
              </>
            )
            return (
              <li
                key={notification.id}
                className={notification.is_read ? 'p-4' : 'bg-primary-50/40 p-4'}
              >
                {href ? (
                  <Link
                    to={href}
                    onClick={() => {
                      if (!notification.is_read) markRead.mutate(notification.id)
                    }}
                    className="block hover:bg-gray-50"
                  >
                    {body}
                  </Link>
                ) : (
                  body
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}