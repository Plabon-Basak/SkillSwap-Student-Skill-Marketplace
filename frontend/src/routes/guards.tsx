import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '@/hooks/useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-gray-500">
        Loading…
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Email must be verified before using marketplace features, except for the
  // verification page itself.
  if (user && !user.email_verified && location.pathname !== '/email-verification') {
    return <Navigate to="/email-verification" replace />
  }

  return <Outlet />
}

export function AdminRoute() {
  const { user } = useAuth()

  if (!user?.email_verified) {
    return <Navigate to="/email-verification" replace />
  }
  if (!user.is_staff) {
    return <Navigate to="/" replace />
  }
  return <Outlet />
}