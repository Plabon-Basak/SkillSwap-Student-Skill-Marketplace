import { Navigate, Route, Routes } from 'react-router-dom'

import { Layout } from '@/components/layout/Layout'
import { useAuth } from '@/hooks/useAuth'
import { AdminRoute, ProtectedRoute } from '@/routes/guards'
import { AdminDashboard } from '@/pages/admin/AdminDashboard'
import { ConversationPage } from '@/pages/ConversationPage'
import { EmailVerificationPage } from '@/pages/EmailVerificationPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { HomePage } from '@/pages/HomePage'
import { ListingDetailPage } from '@/pages/ListingDetailPage'
import { ListingFormPage } from '@/pages/ListingFormPage'
import { LoginPage } from '@/pages/LoginPage'
import { MarketplacePage } from '@/pages/MarketplacePage'
import { MessagesPage } from '@/pages/MessagesPage'
import { MyApplicationsPage } from '@/pages/MyApplicationsPage'
import { MyListingsPage } from '@/pages/MyListingsPage'
import { NotificationsPage } from '@/pages/NotificationsPage'
import { OrderDetailPage } from '@/pages/OrderDetailPage'
import { OrdersPage } from '@/pages/OrdersPage'
import { ProfileEditPage } from '@/pages/ProfileEditPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { PublicProfilePage } from '@/pages/PublicProfilePage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ReportsPage } from '@/pages/ReportsPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { ListingApplicationsPage } from '@/pages/ListingApplicationsPage'

export function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />

        {/* Public auth */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />}
        />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* Public marketplace */}
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/listing/:slug" element={<ListingDetailPage />} />
        <Route path="/profile/:username" element={<PublicProfilePage />} />

        {/* Authenticated */}
        <Route element={<ProtectedRoute />}>
          <Route path="/email-verification" element={<EmailVerificationPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/profile/edit" element={<ProfileEditPage />} />
          <Route path="/listings/mine" element={<MyListingsPage />} />
          <Route path="/listings/new" element={<ListingFormPage />} />
          <Route path="/listings/:slug/edit" element={<ListingFormPage />} />
          <Route
            path="/listings/:slug/applications"
            element={<ListingApplicationsPage />}
          />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/messages" element={<MessagesPage />} />
          <Route path="/messages/:threadId" element={<ConversationPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/applications" element={<MyApplicationsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
        </Route>

        {/* Admin */}
        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/reports" element={<ReportsPage admin />} />
          <Route path="/admin/listings" element={<AdminDashboard />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}