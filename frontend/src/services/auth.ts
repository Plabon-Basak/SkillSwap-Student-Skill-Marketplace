import { api } from '@/api/client'
import type { LoginResponse } from '@/types'

export const authService = {
  async register(payload: {
    username: string
    email: string
    password: string
    first_name?: string
    last_name?: string
  }) {
    return api.post('/auth/register/', payload)
  },
  async login(identifier: string, password: string) {
    const { data } = await api.post<LoginResponse>('/auth/login/', {
      identifier,
      password,
    })
    return data
  },
  async logout(refresh: string) {
    return api.post('/auth/logout/', { refresh })
  },
  async requestEmailVerification() {
    return api.post('/auth/email/verification/request/')
  },
  async verifyEmail(code: string) {
    return api.post('/auth/email/verification/verify/', { code })
  },
  async requestPasswordReset(email: string) {
    return api.post('/auth/password-reset/request/', { email })
  },
  async resetPassword(email: string, code: string, new_password: string) {
    return api.post('/auth/password-reset/verify/', {
      email,
      code,
      new_password,
    })
  },
}