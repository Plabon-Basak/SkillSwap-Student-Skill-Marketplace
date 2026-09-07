import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { useAuth } from '@/hooks/useAuth'
import { notificationsApi } from '@/services/notifications'
import { classNames } from '@/utils/format'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  classNames(
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-white/10 text-white' : 'text-gray-300 hover:bg-white/5 hover:text-white',
  )

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const { data: unreadCount = 0 } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: notificationsApi.unreadCount,
    enabled: isAuthenticated,
    refetchInterval: 30_000,
  })

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <header className="bg-gray-900">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2 text-white">
          <span className="text-lg font-semibold tracking-tight">SkillSwap</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          <NavLink to="/marketplace" className={navLinkClass}>
            Marketplace
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/orders" className={navLinkClass}>
                Orders
              </NavLink>
              <NavLink to="/messages" className={navLinkClass}>
                Messages
              </NavLink>
              <NavLink to="/notifications" className={navLinkClass}>
                <span className="relative inline-flex items-center">
                  Notifications
                  {unreadCount > 0 && (
                    <span className="ml-1.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-medium text-white">
                      {unreadCount}
                    </span>
                  )}
                </span>
              </NavLink>
              {user?.email_verified && (
                <NavLink to="/listings/new" className={navLinkClass}>
                  Sell a skill
                </NavLink>
              )}
            </>
          )}
        </nav>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link
                to="/profile"
                className="hidden text-sm font-medium text-gray-300 hover:text-white sm:block"
              >
                {user?.username}
              </Link>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:text-white"
              >
                Sign out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:text-white"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-md bg-white px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>

      <nav className="border-t border-white/10 md:hidden" aria-label="Mobile">
        <div className="flex overflow-x-auto px-2 py-1.5">
          <NavLink to="/marketplace" className={navLinkClass}>
            Market
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/orders" className={navLinkClass}>
                Orders
              </NavLink>
              <NavLink to="/messages" className={navLinkClass}>
                Messages
              </NavLink>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}