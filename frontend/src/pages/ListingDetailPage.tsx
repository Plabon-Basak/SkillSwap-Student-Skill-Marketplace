import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Avatar, mediaUrl } from '@/components/common/Avatar'
import { Button } from '@/components/common/Button'
import { Alert, EmptyState, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Stars } from '@/components/common/Stars'
import { Field, Textarea } from '@/components/common/Field'
import { useAuth } from '@/hooks/useAuth'
import { listingApi } from '@/services/listings'
import { reportApi } from '@/services/reports'
import { reviewApi } from '@/services/reviews'
import type { Review } from '@/types'
import { formatCurrency, formatRelative } from '@/utils/format'

const applicationSchema = z.object({
  message: z.string().max(500).optional(),
  proposed_price: z.coerce
    .number()
    .min(0, 'Price cannot be negative.')
    .max(999999.99)
    .optional(),
})

type ApplicationForm = z.infer<typeof applicationSchema>

export function ListingDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [reportReason, setReportReason] = useState('')
  const [reportOpen, setReportOpen] = useState(false)
  const [feedback, setFeedback] = useState<{
    kind: 'success' | 'error'
    message: string
  } | null>(null)

  const { data: listing, isLoading, isError } = useQuery({
    queryKey: ['listing', slug],
    queryFn: () => listingApi.get(slug!),
    enabled: Boolean(slug),
  })

  const { data: reviews } = useQuery({
    queryKey: ['reviews', 'listing-provider', listing?.provider.username],
    queryFn: () => reviewApi.forProfile(listing!.provider.username),
    enabled: Boolean(listing),
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ApplicationForm>({ resolver: zodResolver(applicationSchema) })

  const applyMutation = useMutation({
    mutationFn: (values: ApplicationForm) =>
      listingApi.apply(slug!, values.message ?? '', values.proposed_price?.toString()),
    onSuccess: (data) => {
      reset()
      setFeedback({ kind: 'success', message: `Application submitted (id ${data.id}).` })
      void queryClient.invalidateQueries({ queryKey: ['applications'] })
    },
    onError: (error) =>
      setFeedback({ kind: 'error', message: getErrorMessage(error) }),
  })

  const reportMutation = useMutation({
    mutationFn: () =>
      reportApi.create({
        target_type: 'listing',
        target_id: listing!.id,
        reason: reportReason || 'inappropriate',
        description: 'Reported from the listing page.',
      }),
    onSuccess: () => {
      setReportOpen(false)
      setFeedback({ kind: 'success', message: 'Listing reported. Thanks for keeping SkillSwap safe.' })
    },
    onError: (error) => setFeedback({ kind: 'error', message: getErrorMessage(error) }),
  })

  if (isLoading) return <LoadingState />
  if (isError || !listing) return <ErrorState message="Listing not found." />
  if (!listing.is_active) {
    return (
      <EmptyState
        title="This listing is no longer available"
        description="The provider may have retired or suspended it."
        action={<Link to="/marketplace">Back to marketplace</Link>}
      />
    )
  }

  const image = mediaUrl(listing.cover_image)
  const isOwn = user?.username === listing.provider.username

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
      <div>
        <Link
          to="/marketplace"
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          ← Back to marketplace
        </Link>

        <div className="mt-3 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <div className="aspect-[16/9] w-full bg-gray-100">
            {image ? (
              <img src={image} alt="" className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full items-center justify-center text-5xl">
                {listing.category?.name?.[0] ?? '📦'}
              </div>
            )}
          </div>
          <div className="p-5">
            <p className="text-xs font-medium uppercase tracking-wide text-primary-600">
              {listing.category?.name ?? 'General'}
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-gray-900">
              {listing.title}
            </h1>
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-gray-600">
              {listing.description}
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {listing.skills.map((skill) => (
                <span
                  key={skill.id}
                  className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700"
                >
                  {skill.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Provider card */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-gray-900">Offered by</h2>
          <Link
            to={`/profile/${listing.provider.username}`}
            className="mt-3 flex items-center gap-3 hover:opacity-90"
          >
            <Avatar
              src={listing.provider.avatar}
              name={listing.provider.display_name}
              size="lg"
            />
            <div>
              <p className="font-medium text-gray-900">
                {listing.provider.display_name}
                {listing.provider.is_verified_student && (
                  <span className="ml-2 text-xs font-medium text-green-700">
                    ✓ Verified student
                  </span>
                )}
              </p>
              <Stars rating={null} />
            </div>
          </Link>
        </div>

        {/* Reviews */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-gray-900">Reviews</h2>
          {reviews && reviews.length > 0 ? (
            <ul className="mt-3 space-y-3">
              {reviews.slice(0, 10).map((review: Review) => (
                <li key={review.id} className="border-t border-gray-100 pt-3">
                  <div className="flex items-center gap-2">
                    <Stars rating={review.rating} />
                    <span className="text-xs text-gray-500">
                      {review.reviewer.display_name} · {formatRelative(review.created_at)}
                    </span>
                  </div>
                  {review.comment && (
                    <p className="mt-1 text-sm text-gray-600">{review.comment}</p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-gray-500">No reviews yet.</p>
          )}
        </div>
      </div>

      {/* Sidebar */}
      <aside className="space-y-4">
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <p className="text-3xl font-bold text-gray-900">
            {formatCurrency(listing.price, listing.currency)}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            {listing.delivery_time_days
              ? `Delivery in ${listing.delivery_time_days} days`
              : 'Flexible delivery'}
            {' · '}
            {listing.is_remote ? 'Remote' : 'In person'}
            {listing.location && ` · ${listing.location}`}
          </p>

          {feedback && (
            <div className="mt-3">
              <Alert variant={feedback.kind}>{feedback.message}</Alert>
            </div>
          )}

          {isOwn ? (
            <div className="mt-4 space-y-2">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => navigate(`/listings/${listing.slug}/edit`)}
              >
                Edit listing
              </Button>
              <Link
                to={`/listings/${listing.slug}/applications`}
                className="block text-center text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                View applications
              </Link>
            </div>
          ) : isAuthenticated ? (
            <form
              onSubmit={handleSubmit((values) => applyMutation.mutate(values))}
              className="mt-4 space-y-3"
            >
              <Field label="Message to the seller" error={errors.message?.message}>
                <Textarea
                  rows={3}
                  placeholder="Describe what you need…"
                  invalid={Boolean(errors.message)}
                  {...register('message')}
                />
              </Field>
              <Field
                label="Proposed price (optional)"
                error={errors.proposed_price?.message}
              >
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  {...register('proposed_price')}
                />
              </Field>
              <Button type="submit" loading={applyMutation.isPending} className="w-full" disabled={!user?.email_verified}>
                Apply for this service
              </Button>
              {!user?.email_verified && (
                <p className="text-center text-xs text-gray-500">
                  Verify your email before applying.
                </p>
              )}
            </form>
          ) : (
            <div className="mt-4">
              <Link
                to="/login"
                state={{ from: { pathname: `/listing/${listing.slug}` } }}
                className="block w-full text-center"
              >
                <Button variant="primary" className="w-full">
                  Log in to apply
                </Button>
              </Link>
            </div>
          )}
        </div>

        {!isOwn && (
          <div className="rounded-xl border border-gray-200 bg-white p-4">
            {reportOpen ? (
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Reason</label>
                <input
                  type="text"
                  className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm"
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  placeholder="e.g. Spam, scam, inappropriate"
                />
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="danger"
                    loading={reportMutation.isPending}
                    onClick={() => reportMutation.mutate()}
                  >
                    Submit report
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setReportOpen(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setReportOpen(true)}
                className="text-sm text-gray-500 hover:text-red-600"
              >
                Report this listing
              </button>
            )}
          </div>
        )}
      </aside>
    </div>
  )
}