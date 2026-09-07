import { api } from '@/api/client'
import type { PublicProfile, SelfProfile, Skill, User } from '@/types'

export interface ProfileInput {
  first_name?: string
  last_name?: string
  university?: string
  department?: string
  bio?: string
  location?: string
  experience_years?: number
  skills?: string[]
  is_searchable?: boolean
  avatar?: File
}

export const profileApi = {
  async me() {
    const { data } = await api.get<User>('/auth/me/')
    return data
  },
  async getProfile() {
    const { data } = await api.get<SelfProfile>('/profiles/me/')
    return data
  },
  async createProfile(payload: ProfileInput) {
    const form = toFormData(payload)
    const { data } = await api.post<SelfProfile>('/profiles/me/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async updateProfile(payload: ProfileInput) {
    const form = toFormData(payload)
    const { data } = await api.patch<SelfProfile>('/profiles/me/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
  async list(params: Record<string, string>) {
    const { data } = await api.get('/profiles/', { params })
    return data
  },
  async getByUsername(username: string) {
    const { data } = await api.get<PublicProfile>(`/profiles/${username}/`)
    return data
  },
  async skills(search?: string) {
    const { data } = await api.get<Skill[]>('/skills/', { params: { search } })
    return data
  },
}

function toFormData(payload: ProfileInput): FormData {
  const form = new FormData()
  const entries: [string, string | number | Blob][] = [
    ['first_name', payload.first_name ?? ''],
    ['last_name', payload.last_name ?? ''],
    ['university', payload.university ?? ''],
    ['department', payload.department ?? ''],
    ['bio', payload.bio ?? ''],
    ['location', payload.location ?? ''],
    ['experience_years', payload.experience_years ?? 0],
    ['is_searchable', payload.is_searchable ? 'true' : 'false'],
  ]
  for (const [key, value] of entries) {
    form.append(key, String(value))
  }
  for (const skill of payload.skills ?? []) {
    form.append('skills', skill)
  }
  if (payload.avatar) {
    form.append('avatar', payload.avatar)
  }
  return form
}