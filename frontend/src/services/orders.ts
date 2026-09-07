import { api } from '@/api/client'
import type { CheckoutSession, Order, Paginated } from '@/types'

export type OrderAction = 'cancel' | 'start' | 'complete'

export const orderApi = {
  async list(role?: 'buyer' | 'provider', page = 1) {
    const { data } = await api.get<Paginated<Order>>('/orders/', {
      params: { role, page },
    })
    return data
  },
  async get(id: number) {
    const { data } = await api.get<Order>(`/orders/${id}/`)
    return data
  },
  async create(application: number, note = '') {
    const { data } = await api.post<Order>('/orders/', { application, note })
    return data
  },
  async transition(id: number, action: OrderAction) {
    const { data } = await api.patch<Order>(`/orders/${id}/`, { action })
    return data
  },
  async checkout(id: number) {
    const { data } = await api.post<CheckoutSession>(`/orders/${id}/checkout/`)
    return data
  },
  async mockConfirm(id: number) {
    const { data } = await api.post<Order>(`/orders/${id}/mock-confirm/`)
    return data
  },
}

export const ORDER_STATUS_LABELS: Record<Order['status'], string> = {
  pending_payment: 'Pending payment',
  paid: 'Paid',
  in_progress: 'In progress',
  completed: 'Completed',
  cancelled: 'Cancelled',
  refunded: 'Refunded',
}