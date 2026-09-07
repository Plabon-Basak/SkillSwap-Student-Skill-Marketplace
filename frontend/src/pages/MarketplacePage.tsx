import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useDeferredValue, useState, type FormEvent } from 'react'

import { Button } from '@/components/common/Button'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Field, Input, Select } from '@/components/common/Field'
import { Pagination } from '@/components/common/Pagination'
import { ListingCard } from '@/components/listings/ListingCard'
import { listingApi } from '@/services/listings'

const PAGE_SIZE = 12

export function MarketplacePage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchInput, setSearchInput] = useState(searchParams.get('q') ?? '')
  const deferredSearch = useDeferredValue(searchInput)

  const page = Number(searchParams.get('page') ?? 1)
  const category = searchParams.get('category') ?? ''
  const minPrice = searchParams.get('min_price') ?? ''
  const maxPrice = searchParams.get('max_price') ?? ''
  const remote = searchParams.get('remote') ?? ''
  const sort = searchParams.get('sort') ?? 'newest'

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: listingApi.categories,
  })

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: [
      'listings',
      'search',
      { page, category, minPrice, maxPrice, remote, sort, q: deferredSearch },
    ],
    queryFn: () =>
      listingApi.list({
        q: deferredSearch || undefined,
        category: category || undefined,
        min_price: minPrice || undefined,
        max_price: maxPrice || undefined,
        remote: remote ? (remote as 'true' | 'false') : undefined,
        sort: sort as 'newest' | 'price_asc' | 'price_desc',
        page,
      }),
    placeholderData: (prev) => prev,
  })

  const totalPages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1

  const updateParams = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    next.delete('page')
    setSearchParams(next)
  }

  const handleSearch = (event: FormEvent) => {
    event.preventDefault()
    updateParams('q', searchInput.trim())
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Marketplace</h1>
        <p className="mt-1 text-sm text-gray-500">
          Discover services offered by students at your university and beyond.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        {/* Filters */}
        <aside className="space-y-4">
          <form onSubmit={handleSearch}>
            <Field label="Search" hint="Title, description, skills…">
              <Input
                type="search"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="e.g. Python tutoring"
              />
            </Field>
            <Button type="submit" size="sm" className="mt-2">
              Search
            </Button>
          </form>

          <Field label="Category">
            <Select
              value={category}
              onChange={(e) => updateParams('category', e.target.value)}
            >
              <option value="">All categories</option>
              {categories?.map((c) => (
                <option key={c.id} value={c.slug}>
                  {c.name}
                </option>
              ))}
            </Select>
          </Field>

          <div className="grid grid-cols-2 gap-2">
            <Field label="Min price">
              <Input
                type="number"
                min="0"
                step="0.01"
                value={minPrice}
                onChange={(e) => updateParams('min_price', e.target.value)}
                placeholder="$0"
              />
            </Field>
            <Field label="Max price">
              <Input
                type="number"
                min="0"
                step="0.01"
                value={maxPrice}
                onChange={(e) => updateParams('max_price', e.target.value)}
                placeholder="$100"
              />
            </Field>
          </div>

          <Field label="Delivery">
            <Select
              value={remote}
              onChange={(e) => updateParams('remote', e.target.value)}
            >
              <option value="">Any</option>
              <option value="true">Remote only</option>
              <option value="false">In person only</option>
            </Select>
          </Field>

          <Field label="Sort by">
            <Select value={sort} onChange={(e) => updateParams('sort', e.target.value)}>
              <option value="newest">Newest first</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </Select>
          </Field>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => {
              setSearchInput('')
              setSearchParams(new URLSearchParams(), { replace: true })
            }}
          >
            Clear filters
          </Button>
        </aside>

        {/* Results */}
        <section>
          {isLoading ? (
            <LoadingState label="Searching the marketplace…" />
          ) : isError ? (
            <ErrorState
              message="Could not load listings."
              onRetry={() => void refetch()}
            />
          ) : data && data.results.length > 0 ? (
            <>
              <p className="mb-3 text-sm text-gray-500">
                {data.count} service{data.count === 1 ? '' : 's'} found
              </p>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {data.results.map((listing) => (
                  <ListingCard key={listing.id} listing={listing} />
                ))}
              </div>
              <Pagination
                page={page}
                totalPages={totalPages}
                onChange={(next) => updateParams('page', String(next))}
              />
            </>
          ) : (
            <EmptyState
              title="No services match your search"
              description="Try different keywords or remove some filters."
            />
          )}
        </section>
      </div>
    </div>
  )
}