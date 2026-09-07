import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { LoadingState } from '@/components/common/Feedback'
import { ListingCard } from '@/components/listings/ListingCard'
import { useAuth } from '@/hooks/useAuth'
import { listingApi } from '@/services/listings'

export function HomePage() {
  const { isAuthenticated } = useAuth()

  const { data, isLoading } = useQuery({
    queryKey: ['listings', 'featured'],
    queryFn: () => listingApi.list({ sort: 'newest', page: 1 }),
  })

  return (
    <div>
      <section className="rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 px-6 py-14 text-white shadow-lg">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Skills your classmates offer, ready to learn.
          </h1>
          <p className="mt-3 text-base text-primary-100">
            SkillSwap connects students who want to share what they know. Offer
            tutoring, design, coding, video editing and more — or find the skill
            you need.
          </p>
          <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
            <Link
              to="/marketplace"
              className="rounded-md bg-white px-5 py-2.5 text-sm font-semibold text-primary-700 hover:bg-primary-50"
            >
              Browse the marketplace
            </Link>
            {isAuthenticated ? (
              <Link
                to="/listings/new"
                className="rounded-md border border-white/40 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
              >
                Offer a skill
              </Link>
            ) : (
              <Link
                to="/register"
                className="rounded-md border border-white/40 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
              >
                Create an account
              </Link>
            )}
          </div>
        </div>
      </section>

      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Newest services</h2>
          <Link
            to="/marketplace"
            className="text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            View all →
          </Link>
        </div>

        {isLoading ? (
          <LoadingState />
        ) : data && data.results.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data.results.slice(0, 8).map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        ) : (
          <p className="py-10 text-center text-gray-500">
            No services published yet. Be the first to offer a skill!
          </p>
        )}
      </section>

      <section className="mt-12 grid gap-4 sm:grid-cols-3">
        {[
          {
            title: 'Learn',
            body: 'Book a session with a student who excels at the skill you want to master.',
          },
          {
            title: 'Earn',
            body: 'Turn your expertise into income by publishing services and accepting orders.',
          },
          {
            title: 'Connect',
            body: 'Message buyers and sellers directly to agree on requirements before starting.',
          },
        ].map((item) => (
          <div
            key={item.title}
            className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
          >
            <h3 className="text-base font-semibold text-gray-900">{item.title}</h3>
            <p className="mt-1 text-sm text-gray-500">{item.body}</p>
          </div>
        ))}
      </section>
    </div>
  )
}