export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  email_verified: boolean
  date_joined: string
  is_staff: boolean
}

export interface Skill {
  id: number
  name: string
  slug: string
}

export interface ProviderSummary {
  username: string
  display_name: string
  avatar: string | null
  is_verified_student: boolean
}

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
}

export interface Listing {
  id: number
  slug: string
  title: string
  description: string
  provider: ProviderSummary
  category: Category | null
  skills: Skill[]
  price: string
  currency: string
  delivery_time_days: number | null
  is_remote: boolean
  location: string
  cover_image: string | null
  is_active: boolean
  is_archived: boolean
  moderation_status: 'draft' | 'pending' | 'published' | 'rejected' | 'suspended' | 'archived'
  created_at: string
  updated_at: string
}

export interface Application {
  id: number
  listing: {
    id: number
    slug: string
    title: string
    price: string
    currency: string
    cover_image: string | null
  }
  applicant: ProviderSummary
  message: string
  proposed_price: string | null
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn'
  responded_at: string | null
  created_at: string
}

export interface Order {
  id: number
  application: number
  listing: {
    id: number
    slug: string
    title: string
    price: string
    currency: string
    cover_image: string | null
  } | null
  buyer: ProviderSummary
  provider: ProviderSummary
  price: string
  currency: string
  note: string
  status:
    | 'pending_payment'
    | 'paid'
    | 'in_progress'
    | 'completed'
    | 'cancelled'
    | 'refunded'
  paid_at: string | null
  started_at: string | null
  completed_at: string | null
  cancelled_at: string | null
  created_at: string
}

export interface PublicProfile {
  id: number
  username: string
  display_name: string
  avatar: string | null
  university: string
  department: string
  is_student: boolean
  bio: string
  location: string
  experience_years: number
  skills: Skill[]
  is_verified_student: boolean
  member_since: string
  rating_average: number | null
  rating_count: number
}

export interface SelfProfile extends PublicProfile {
  email: string
  email_verified: boolean
  first_name: string
  last_name: string
  is_searchable: boolean
  created_at: string
  updated_at: string
}

export interface Thread {
  id: number
  order: number
  buyer: ProviderSummary
  provider: ProviderSummary
  last_message_at: string | null
  unread_count: number
  created_at: string
}

export interface Message {
  id: number
  sender: ProviderSummary
  body: string
  is_read: boolean
  created_at: string
}

export interface Notification {
  id: number
  verb: string
  actor_username: string | null
  target_type: string
  target_id: number | null
  data: Record<string, unknown>
  is_read: boolean
  created_at: string
}

export interface Review {
  id: number
  order: number
  reviewer: ProviderSummary
  rating: number
  comment: string
  created_at: string
}

export interface Report {
  id: number
  reporter: User
  target_type: 'user' | 'listing' | 'message' | 'review'
  target_id: number
  target_name: string | null
  reason: string
  description: string
  status: 'pending' | 'reviewing' | 'resolved' | 'rejected'
  admin_notes: string
  reviewed_by: { id: number; username: string } | null
  resolved_at: string | null
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface CheckoutSession {
  session_id: string
  url: string
  mode: 'simulation' | 'stripe'
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface AuthTokens {
  access: string
  refresh: string
  accessExpiresAt: number
}