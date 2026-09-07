import { api } from '@/api/client'
import type { Paginated } from '@/types'

export interface Notification {
  id: number
  verb: string
  actor_username: string | null
  target_type: string
  target_id: number | null
  data: Record<string, unknown>
  is_read: boolean
  created_at: string
}

export const notificationsApi = {
  async list(unreadOnly = false) {
    const { data } = await api.get<Paginated<Notification>>(
      '/notifications/mine/',
      { params: { unread: unreadOnly ? 'true' : undefined } },
    )
    return data
  },
  async unreadCount() {
    const { data } = await api.get<{ count: number }>(
      '/notifications/unread-count/',
    )
    return data.count
  },
  async markRead(id: number) {
    const { data } = await api.post(`/notifications/${id}/read/`)
    return data
  },
  async markAllRead() {
    const { data } = await api.post('/notifications/read-all/')
    return data
  },
}