import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { Avatar } from '@/components/common/Avatar'
import { Button } from '@/components/common/Button'
import { Card, PageHeader, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Stars } from '@/components/common/Stars'
import { profileApi } from '@/services/profiles'
import { formatDate } from '@/utils/format'

export function ProfilePage() {
  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: profileApi.getProfile,
  })

  if (isLoading) return <LoadingState />
  if (isError || !profile) return <ErrorState message="Could not load your profile." />

  return (
    <div>
      <PageHeader
        title={profile.display_name}
        subtitle="Your public profile. Students see this page when they click your name."
        actions={
          <Link to="/profile/edit">
            <Button>Edit profile</Button>
          </Link>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <div className="flex flex-col items-center text-center">
            <Avatar src={profile.avatar} name={profile.display_name} size="lg" />
            <h2 className="mt-3 text-lg font-semibold text-gray-900">
              {profile.display_name}
            </h2>
            <p className="text-sm text-gray-500">@{profile.username}</p>
            {profile.is_verified_student && (
              <span className="mt-1 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                Verified student
              </span>
            )}
            <div className="mt-3">
              <Stars rating={profile.rating_average} count={profile.rating_count} />
            </div>
          </div>

          <dl className="mt-5 space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">University</dt>
              <dd className="font-medium text-gray-900">{profile.university || '—'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Department</dt>
              <dd className="font-medium text-gray-900">{profile.department || '—'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Experience</dt>
              <dd className="font-medium text-gray-900">
                {profile.experience_years
                  ? `${profile.experience_years} year${profile.experience_years === 1 ? '' : 's'}`
                  : '—'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Member since</dt>
              <dd className="font-medium text-gray-900">{formatDate(profile.member_since)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Searchable</dt>
              <dd className="font-medium text-gray-900">
                {profile.is_searchable ? 'Yes' : 'No'}
              </dd>
            </div>
          </dl>
        </Card>

        <div className="space-y-6">
          <Card>
            <h3 className="text-sm font-semibold text-gray-900">Bio</h3>
            <p className="mt-2 whitespace-pre-line text-sm text-gray-600">
              {profile.bio || 'No bio yet.'}
            </p>
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-gray-900">Skills</h3>
            {profile.skills.length > 0 ? (
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
            ) : (
              <p className="mt-2 text-sm text-gray-500">No skills added yet.</p>
            )}
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-gray-900">Quick links</h3>
            <ul className="mt-2 space-y-1 text-sm">
              <li>
                <Link to="/listings/mine" className="text-primary-600 hover:text-primary-700">
                  My services
                </Link>
              </li>
              <li>
                <Link to="/applications" className="text-primary-600 hover:text-primary-700">
                  My applications
                </Link>
              </li>
              <li>
                <Link to="/orders" className="text-primary-600 hover:text-primary-700">
                  Orders
                </Link>
              </li>
              <li>
                <Link
                  to={`/profile/${profile.username}`}
                  className="text-primary-600 hover:text-primary-700"
                >
                  Public profile
                </Link>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  )
}