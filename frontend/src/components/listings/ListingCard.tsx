import { Link } from 'react-router-dom'

import { mediaUrl } from '@/components/common/Avatar'
import type { Listing } from '@/types'
import { formatCurrency, truncate } from '@/utils/format'

export function ListingCard({ listing }: { listing: Listing }) {
  const image = mediaUrl(listing.cover_image)
  return (
    <Link
      to={`/listing/${listing.slug}`}
      className="group flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="aspect-[4/3] w-full overflow-hidden bg-gray-100">
        {image ? (
          <img
            src={image}
            alt=""
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-4xl">
            {listing.category?.name?.[0] ?? '📦'}
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-1.5 p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-primary-600">
          {listing.category?.name ?? 'General'}
        </p>
        <h3 className="line-clamp-2 text-sm font-semibold text-gray-900">
          {listing.title}
        </h3>
        <p className="line-clamp-2 text-xs text-gray-500">
          {truncate(listing.description, 80)}
        </p>
        <div className="mt-auto flex items-center justify-between pt-2">
          <span className="text-base font-bold text-gray-900">
            {formatCurrency(listing.price, listing.currency)}
          </span>
          <span className="text-xs text-gray-500">
            {listing.delivery_time_days
              ? `Delivered in ${listing.delivery_time_days}d`
              : 'Flexible'}
          </span>
        </div>
        <div className="flex items-center gap-2 border-t border-gray-100 pt-2">
          <span className="ml-auto truncate text-xs text-gray-500">
            {listing.provider.display_name}
          </span>
        </div>
      </div>
    </Link>
  )
}