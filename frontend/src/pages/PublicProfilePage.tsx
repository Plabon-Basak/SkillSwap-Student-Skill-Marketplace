import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { getErrorMessage } from '@/api/client'
import { Avatar, mediaUrl } from '@/components/common/Avatar'
import { Button } from '@/components/common/Button'
import { Alert, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Stars } from '@/components/common/Stars'
import { useAuth } from '@/hooks/useAuth'
import { listingApi } from '@/services/listings'
import { profileApi } from '@/services/profiles'
import { reportApi } from '@/services/reports'
import { reviewApi } from '@/services/reviews'
import { formatDate } from '@/utils/format'

export function PublicProfilePage() {
  const { username } = useParams<{ username: string }>()
  const { user } = useAuth()
  const [reportReason, setReportReason] = useState('')
  const [reportOpen, setReportOpen] = useState(false)
  const [feedback, setFeedback] = useState<{
    kind: 'success' | 'error'
    message: string
  } | null>(null)

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['profile', username],
    queryFn: () => profileApi.getByUsername(username!),
    enabled: Boolean(username),
  })

  const { data: listings } = useQuery({
    queryKey: ['listings', 'by', username],
    queryFn: () => listingApi.list({ provider: username!, sort: 'newest' }),
    enabled: Boolean(username),
  })

  const { data: reviews } = useQuery({
    queryKey: ['reviews', 'profile', username],
    queryFn: () => reviewApi.forProfile(username!),
    enabled: Boolean(username),
  })

  const reportMutation = useMutation({
    mutationFn: () =>
      reportApi.create({
        target_type: 'user',
        target_id: profile!.id,
        reason: reportReason || 'suspicious',
        description: 'Reported from the public profile page.',
      }),
    onSuccess: () => {
      setReportOpen(false)
      setFeedback({ kind: 'success', message: 'User reported. Thanks for keeping SkillSwap safe.' })
    },
    onError: (error) => setFeedback({ kind: 'error', message: getErrorMessage(error) }),
  })

  if (isLoading) return <LoadingState />
  if (isError || !profile) return <ErrorState message="User not found." />

  const isOwn = user?.username === profile.username
  const published = listings?.results ?? []

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
      <div>
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <div className="h-28 bg-gradient-to-r from-primary-600 to-primary-400" />
          <div className="p-5">
            <div className="-mt-16">
              <Avatar src={profile.avatar} name={profile.display_name} size="xl" />
            </div>
            <div className="mt-3">
              <h1 className="text-2xl font-semibold text-gray-900">{profile.display_name}</h1>
              <p className="text-sm text-gray-500">@{profile.username}</p>
              <div className="mt-1 flex items-center gap-2">
                {profile.is_verified_student && (
                  <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                    Verified student
                  </span>
                )}
              </div>
              <div className="mt-2">
                <Stars rating={profile.rating_average} count={profile.rating_count} />
              </div>
            </div>
          </div>

          <div className="border-t border-gray-100 p-5">
            <h2 className="text-sm font-semibold text-gray-900">About</h2>
            <p className="mt-2 whitespace-pre-line text-sm text-gray-600">
              {profile.bio || 'This student has not written a bio yet.'}
            </p>
            <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-gray-500">University</dt>
                <dd className="font-medium text-gray-900">{profile.university || '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Department</dt>
                <dd className="font-medium text-gray-900">{profile.department || '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Location</dt>
                <dd className="font-medium text-gray-900">{profile.location || '—'}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Member since</dt>
                <dd className="font-medium text-gray-900">{formatDate(profile.member_since)}</dd>
              </div>
            </dl>
            {profile.skills.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-semibold text-gray-900">Skills</p>
                <ul className="mt-2 flex flex-wrap gap-2">
                  {profile.skills.map((skill) => (
                    <li
                      key={skill.id}
                      className="rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700"
                    >
                      {skill.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Services */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-gray-900">
            Services ({published.length})
          </h2>
          {published.length > 0 ? (
            <ul className="mt-3 space-y-3">
              {published.map((listing) => (
                <li key={listing.id} className="border-t border-gray-100 pt-3">
                  <a href={`/listing/${listing.slug}`} className="text-sm font-medium text-primary-600 hover:text-primary-700">
                    {listing.title}
                  </a>
                  <p className="mt-0.5 text-xs text-gray-500">
                    {listing.category?.name ?? 'General'} · From ${Number(listing.price).toFixed(2)}
                  </p>
                  {listing.cover_image && (
                    <img
                      src={mediaUrl(listing.cover_image) ?? undefined}
                      alt=""
                      className="mt-2 h-20 w-32 rounded-md object-cover"
                    />
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-gray-500">This student has no published services.</p>
          )}
        </div>

        {/* Reviews */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-gray-900">Reviews</h2>
          {reviews && reviews.length > 0 ? (
            <ul className="mt-3 space-y-3">
              {reviews.slice(0, 10).map((review) => (
                <li key={review.id} className="border-t border-gray-100 pt-3">
                  <div className="flex items-center gap-2">
                    <Stars rating={review.rating} />
                    <span className="text-xs text-gray-500">
                      {review.reviewer.display_name} · {formatDate(review.created_at)}
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

      <aside className="space-y-4">
        {!isOwn ? (
          <>
            {feedback && <Alert variant={feedback.kind}>{feedback.message}</Alert>}

            <div className="rounded-xl border border-gray-200 bg-white p-4">
              {reportOpen ? (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">Reason</label>
                  <input
                    type="text"
                    className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm"
                    value={reportReason}
                    onChange={(e) => setReportReason(e.target.value)}
                    placeholder="e.g. Scam, impersonation, abuse"
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
                  Report this user
                </button>
              )}
            </div>
          </>
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600">
            This is you. <a href="/profile/edit" className="text-primary-600">Edit your profile</a>.
          </div>
        )}
      </aside>
    </div>
  )
}