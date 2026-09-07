import { api } from '@/api/client'
import type { Listing, Paginated, Report } from '@/types'

export const reportApi = {
  async create(payload: {
    target_type: 'user' | 'listing' | 'message' | 'review'
    target_id: number
    reason: string
    description?: string
  }) {
    const { data } = await api.post<Report>('/reports/create/', payload)
    return data
  },
  async list(params?: Record<string, string>) {
    const { data } = await api.get<Paginated<Report>>('/reports/', { params })
    return data
  },
  async detail(id: number) {
    const { data } = await api.get<Report>(`/reports/${id}/`)
    return data
  },
  async review(id: number, action: 'resolve' | 'reject', admin_notes = '') {
    const { data } = await api.post<Report>(`/reports/${id}/`, {
      action,
      admin_notes,
    })
    return data
  },
}

export const adminApi = {
  async moderateUser(id: number, action: 'suspend' | 'reactivate', reason = '') {
    const { data } = await api.post(`/moderation/users/${id}/`, {
      action,
      reason,
    })
    return data
  },
  async listings(status?: string) {
    const { data } = await api.get<Listing[] | Paginated<Listing>>(
      '/moderation/listings/',
      { params: { status } },
    )
    return data
  },
  async moderateListing(
    id: number,
    action: 'approve' | 'reject' | 'suspend' | 'remove',
    note = '',
  ) {
    const { data } = await api.post(`/moderation/listings/${id}/`, {
      action,
      note,
    })
    return data
  },
}