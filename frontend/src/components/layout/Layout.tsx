import { Outlet } from 'react-router-dom'

import { Navbar } from '@/components/layout/Navbar'

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 text-center text-sm text-gray-500">
          SkillSwap — trade skills with students at your university.
        </div>
      </footer>
    </div>
  )
}