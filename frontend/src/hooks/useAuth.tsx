import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { tokenStore } from '@/api/client'
import { authService } from '@/services/auth'
import { profileApi } from '@/services/profiles'
import type { User } from '@/types'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (identifier: string, password: string) => Promise<User>
  logout: () => Promise<void>
  refetchUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refetchUser = useCallback(async () => {
    try {
      const fetched = await profileApi.me()
      setUser(fetched)
    } catch {
      tokenStore.clear()
      setUser(null)
    }
  }, [])

  useEffect(() => {
    let active = true
    const load = async () => {
      if (!tokenStore.getRefreshToken()) {
        if (active) setIsLoading(false)
        return
      }
      await refetchUser()
      if (active) setIsLoading(false)
    }
    void load()

    const onAuthExpired = () => {
      if (active) setUser(null)
    }
    window.addEventListener('skillswap:auth-expired', onAuthExpired)
    return () => {
      active = false
      window.removeEventListener('skillswap:auth-expired', onAuthExpired)
    }
  }, [refetchUser])

  const login = useCallback(async (identifier: string, password: string) => {
    const data = await authService.login(identifier, password)
    tokenStore.set({
      access: data.access,
      refresh: data.refresh,
      accessExpiresAt: Date.now() + 30 * 60 * 1000,
    })
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(async () => {
    const refresh = tokenStore.getRefreshToken()
    if (refresh) {
      try {
        await authService.logout(refresh)
      } catch {
        // Surface an error in the UI; local state still clears.
      }
    }
    tokenStore.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      refetchUser,
    }),
    [user, isLoading, login, logout, refetchUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider.')
  return ctx
}