import { api } from '@/api/client'
import type { Message, Thread } from '@/types'

export const messagingApi = {
  async threads() {
    const { data } = await api.get<Thread[]>('/threads/mine/')
    return data
  },
  async thread(id: number) {
    const { data } = await api.get<Thread>(`/threads/${id}/`)
    return data
  },
  async messages(threadId: number) {
    const { data } = await api.get<Message[]>(`/threads/${threadId}/messages/`)
    return data
  },
  async sendMessage(threadId: number, body: string) {
    const { data } = await api.post<Message>(`/threads/${threadId}/messages/`, {
      body,
    })
    return data
  },
  async unreadCount() {
    const { data } = await api.get<{ count: number }>('/threads/unread-count/')
    return data.count
  },
}