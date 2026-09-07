import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useParams } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Button } from '@/components/common/Button'
import { Alert, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Field, Input, Select, Textarea } from '@/components/common/Field'
import { listingApi, type ListingInput } from '@/services/listings'

const listingSchema = z.object({
  title: z
    .string()
    .min(5, 'Title must be at least 5 characters.')
    .max(120, 'Title must be at most 120 characters.'),
  description: z.string().max(2000).optional(),
  category: z.string().optional(),
  skills: z.string().optional(),
  price: z.coerce.number().min(0, 'Price cannot be negative.').max(99999999),
  currency: z.string(),
  delivery_time_days: z.coerce.number().int().min(1).max(730).optional().or(z.literal('')),
  is_remote: z.boolean(),
  location: z.string().max(120).optional(),
})

type ListingForm = z.infer<typeof listingSchema>

export function ListingFormPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const isEditing = Boolean(slug)
  const [coverImage, setCoverImage] = useState<File | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: listingApi.categories,
  })

  const { data: existing, isLoading } = useQuery({
    queryKey: ['listing', slug],
    queryFn: () => listingApi.get(slug!),
    enabled: isEditing,
  })

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ListingForm>({
    resolver: zodResolver(listingSchema),
    defaultValues: {
      currency: 'USD',
      is_remote: true,
      delivery_time_days: undefined,
    },
  })

  useEffect(() => {
    if (existing) {
      reset({
        title: existing.title,
        description: existing.description,
        category: existing.category?.slug ?? '',
        skills: existing.skills.map((s) => s.name).join(', '),
        price: Number(existing.price),
        currency: existing.currency,
        delivery_time_days: existing.delivery_time_days ?? undefined,
        is_remote: existing.is_remote,
        location: existing.location,
      })
    }
  }, [existing, reset])

  const isRemote = watch('is_remote')

  const saveListing = useMutation({
    mutationFn: async (values: ListingForm) => {
      const payload: ListingInput = {
        title: values.title,
        description: values.description,
        price: String(values.price),
        currency: values.currency,
        is_remote: values.is_remote,
        location: values.location ?? '',
        skills: (values.skills ?? '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      }
      if (values.category) payload.category = values.category
      if (values.delivery_time_days) payload.delivery_time_days = Number(values.delivery_time_days)
      if (coverImage) payload.cover_image = coverImage
      return isEditing && slug
        ? listingApi.update(slug, payload)
        : listingApi.create(payload)
    },
    onSuccess: (listing) => {
      navigate(`/listing/${listing.slug}`, { replace: true })
    },
    onError: (error) => setSubmitError(getErrorMessage(error)),
  })

  const onSubmit = handleSubmit((values) => saveListing.mutate(values))

  if (isEditing && isLoading) return <LoadingState />
  if (isEditing && !existing) return <ErrorState message="Listing not found." />

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold text-gray-900">
        {isEditing ? 'Edit listing' : 'Publish a new service'}
      </h1>
      <p className="mt-1 text-sm text-gray-500">
        Describe the service you offer, set your price, and start receiving applications.
      </p>

      {submitError && (
        <div className="mt-4">
          <Alert variant="error">{submitError}</Alert>
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-6 space-y-5 noValidate">
        <Field label="Title" error={errors.title?.message}>
          <Input
            type="text"
            placeholder="e.g. Python tutoring for beginners"
            invalid={Boolean(errors.title)}
            {...register('title')}
          />
        </Field>

        <Field label="Description" error={errors.description?.message}>
          <Textarea
            rows={5}
            placeholder="What will you deliver? What prerequisites exist?"
            invalid={Boolean(errors.description)}
            {...register('description')}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Category" error={errors.category?.message}>
            <Select {...register('category')}>
              <option value="">No category</option>
              {categories?.map((c) => (
                <option key={c.id} value={c.slug}>
                  {c.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Skills (comma separated)">
            <Input
              type="text"
              placeholder="Python, Data analysis"
              {...register('skills')}
            />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Price" error={errors.price?.message}>
            <Input
              type="number"
              min="0"
              step="0.01"
              invalid={Boolean(errors.price)}
              {...register('price')}
            />
          </Field>
          <Field label="Currency">
            <Select {...register('currency')}>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </Select>
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Delivery time (days, optional)"
            error={errors.delivery_time_days?.message}
          >
            <Input
              type="number"
              min="1"
              max="730"
              invalid={Boolean(errors.delivery_time_days)}
              {...register('delivery_time_days')}
            />
          </Field>
          <Field label="Location (optional)">
            <Input type="text" placeholder="e.g. Main campus" {...register('location')} />
          </Field>
        </div>

        <Field>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              checked={isRemote}
              onChange={(e) => setValue('is_remote', e.target.checked)}
            />
            This service can be delivered remotely
          </label>
        </Field>

        {!isRemote && (
          <p className="text-sm text-gray-500">
            Location will be used by buyers to find you.
          </p>
        )}

        <Field label="Cover image">
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={(e) => setCoverImage(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-gray-500 file:mr-3 file:rounded-md file:border-0 file:bg-primary-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
          />
        </Field>

        <div className="flex items-center gap-3">
          <Button type="submit" loading={isSubmitting || saveListing.isPending}>
            {isEditing ? 'Save changes' : 'Publish service'}
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}