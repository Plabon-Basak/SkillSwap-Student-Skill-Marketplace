import { api } from '@/api/client'
import type { Review } from '@/types'

export const reviewApi = {
  async create(order: number, rating: number, comment: string) {
    const { data } = await api.post<Review>('/reviews/', {
      order,
      rating,
      comment,
    })
    return data
  },
  async forProfile(username: string) {
    const { data } = await api.get<Review[]>(`/profiles/${username}/reviews/`)
    return data
  },
}