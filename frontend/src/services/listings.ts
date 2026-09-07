import { api } from '@/api/client'
import type { Application, Category, Listing, Paginated } from '@/types'

export interface ListingInput {
  title: string
  description?: string
  category?: string
  skills?: string[]
  price: string
  currency?: string
  delivery_time_days?: number | null
  is_remote?: boolean
  location?: string
  cover_image?: File | null
}

export interface ListingQuery {
  q?: string
  category?: string
  skill?: string
  min_price?: string
  max_price?: string
  remote?: 'true' | 'false'
  location?: string
  provider?: string
  sort?: 'newest' | 'price_asc' | 'price_desc'
  page?: number
}

export const listingApi = {
  async list(params: ListingQuery) {
    const { data } = await api.get<Paginated<Listing>>('/listings/', {
      params,
    })
    return data
  },
  async get(slug: string) {
    const { data } = await api.get<Listing>(`/listings/${slug}/`)
    return data
  },
  async create(payload: ListingInput) {
    const form = toFormData(payload)
    const { data } = await api.post<Listing>('/listings/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async update(slug: string, payload: ListingInput) {
    const form = toFormData(payload)
    const { data } = await api.patch<Listing>(`/listings/${slug}/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async remove(slug: string) {
    return api.delete(`/listings/${slug}/`)
  },
  async mine() {
    const { data } = await api.get<Listing[]>('/listings/mine/')
    return data
  },
  async categories() {
    const { data } = await api.get<Category[]>('/categories/')
    return data
  },
  async applicationsFor(slug: string) {
    const { data } = await api.get<Paginated<Application>>(
      `/listings/${slug}/applications/`,
    )
    return data
  },
  async apply(slug: string, message: string, proposed_price?: string) {
    const { data } = await api.post<Application>(
      `/listings/${slug}/applications/`,
      { message, proposed_price },
    )
    return data
  },
  async myApplications() {
    const { data } = await api.get<Paginated<Application>>('/applications/mine/')
    return data
  },
  async respondToApplication(id: number, action: 'accept' | 'reject' | 'withdraw') {
    const { data } = await api.patch<Application>(`/applications/${id}/`, {
      action,
    })
    return data
  },
}

function toFormData(payload: ListingInput): FormData {
  const form = new FormData()
  form.append('title', payload.title)
  form.append('description', payload.description ?? '')
  form.append('price', payload.price)
  form.append('currency', payload.currency ?? 'USD')
  form.append('is_remote', payload.is_remote ? 'true' : 'false')
  form.append('location', payload.location ?? '')
  if (payload.category) form.append('category', payload.category)
  if (payload.delivery_time_days != null) {
    form.append('delivery_time_days', String(payload.delivery_time_days))
  }
  for (const skill of payload.skills ?? []) {
    form.append('skills', skill)
  }
  if (payload.cover_image) {
    form.append('cover_image', payload.cover_image)
  }
  return form
}