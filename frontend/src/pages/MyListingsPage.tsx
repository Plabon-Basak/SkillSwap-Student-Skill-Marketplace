import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { Button } from '@/components/common/Button'
import { EmptyState, LoadingState } from '@/components/common/Feedback'
import { listingApi } from '@/services/listings'

export function MyListingsPage() {
  const queryClient = useQueryClient()
  const { data: listings, isLoading } = useQuery({
    queryKey: ['listings', 'mine'],
    queryFn: listingApi.mine,
  })

  const removeListing = useMutation({
    mutationFn: listingApi.remove,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['listings', 'mine'] }),
  })

  if (isLoading) return <LoadingState />

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">My services</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage the skills you offer on SkillSwap.
          </p>
        </div>
        <Link to="/listings/new">
          <Button>New listing</Button>
        </Link>
      </div>

      {!listings || listings.length === 0 ? (
        <EmptyState
          title="You haven't published any services yet"
          description="Create a listing to start receiving applications and orders."
          action={
            <Link to="/listings/new">
              <Button>Publish a service</Button>
            </Link>
          }
        />
      ) : (
        <ul className="divide-y divide-gray-200 rounded-xl border border-gray-200 bg-white shadow-sm">
          {listings.map((listing) => (
            <li key={listing.id} className="flex items-center justify-between gap-4 p-4">
              <div className="min-w-0">
                <Link
                  to={`/listing/${listing.slug}`}
                  className="font-medium text-gray-900 hover:text-primary-600"
                >
                  {listing.title}
                </Link>
                <p className="mt-0.5 text-sm text-gray-500">
                  ${listing.price} · {listing.is_active ? 'Active' : 'Inactive'}
                  {listing.is_archived ? ' · Archived' : ''}
                </p>
                <p className="text-sm text-gray-500">
                  Applications:{' '}
                  <Link
                    to={`/listings/${listing.slug}/applications`}
                    className="text-primary-600 hover:text-primary-700"
                  >
                    view
                  </Link>
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <Link to={`/listings/${listing.slug}/edit`}>
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                </Link>
                {!listing.is_archived && (
                  <Button
                    variant="danger"
                    size="sm"
                    loading={removeListing.isPending}
                    onClick={() => removeListing.mutate(listing.slug)}
                  >
                    Archive
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}