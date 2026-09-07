import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

const TOKEN_KEY = 'skillswap.tokens'

interface StoredTokens {
  access: string
  refresh: string
  accessExpiresAt: number
}

const isBrowser = typeof window !== 'undefined'

export const tokenStore = {
  get(): StoredTokens | null {
    if (!isBrowser) return null
    const raw = localStorage.getItem(TOKEN_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw) as StoredTokens
    } catch {
      return null
    }
  },
  set(tokens: StoredTokens) {
    if (!isBrowser) return
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens))
  },
  clear() {
    if (!isBrowser) return
    localStorage.removeItem(TOKEN_KEY)
  },
  getAccessToken(): string | null {
    return this.get()?.access ?? null
  },
  getRefreshToken(): string | null {
    return this.get()?.refresh ?? null
  },
  isAccessExpired(): boolean {
    const tokens = this.get()
    if (!tokens) return true
    // Leave a 10-second buffer for clock skew / request in flight.
    return Date.now() >= tokens.accessExpiresAt - 10_000
  },
}

export interface RefreshResponse {
  access: string
  refresh: string
}

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStore.getRefreshToken()
  if (!refresh) throw new Error('No refresh token available.')

  const { data } = await axios.post<RefreshResponse>(`${API_URL}/auth/refresh/`, {
    refresh,
  })
  const accessExpiresAt = Date.now() + 30 * 60 * 1000 // 30 min, matches the backend default.
  tokenStore.set({ access: data.access, refresh: data.refresh, accessExpiresAt })
  return data.access
}

type RetryableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

api.interceptors.request.use((config) => {
  if (!tokenStore.isAccessExpired()) {
    const access = tokenStore.getAccessToken()
    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableConfig | undefined
    const isRefreshRequest =
      original?.url?.includes('/auth/refresh/') ?? false

    if (error.response?.status !== 401 || !original || original._retry || isRefreshRequest) {
      return Promise.reject(error)
    }

    original._retry = true
    try {
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null
      })
      const access = await refreshPromise
      original.headers.Authorization = `Bearer ${access}`
      return api(original)
    } catch {
      tokenStore.clear()
      if (isBrowser) {
        window.dispatchEvent(new CustomEvent('skillswap:auth-expired'))
      }
      return Promise.reject(error)
    }
  },
)

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | undefined
    if (data) {
      if (typeof data.detail === 'string') return data.detail
      const firstKey = Object.keys(data)[0]
      if (firstKey && firstKey !== 'detail') {
        const value = data[firstKey]
        if (Array.isArray(value)) return String(value[0])
        return String(value)
      }
    }
    return error.message ?? 'Request failed.'
  }
  if (error instanceof Error) return error.message
  return 'An unexpected error occurred.'
}