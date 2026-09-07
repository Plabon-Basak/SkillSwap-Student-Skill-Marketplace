import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Button } from '@/components/common/Button'
import { Alert, ErrorState, LoadingState } from '@/components/common/Feedback'
import { Field, Input, Textarea } from '@/components/common/Field'
import { profileApi, type ProfileInput } from '@/services/profiles'
import { classNames } from '@/utils/format'

const profileSchema = z.object({
  first_name: z.string().max(150).optional(),
  last_name: z.string().max(150).optional(),
  university: z.string().max(150).optional(),
  department: z.string().max(150).optional(),
  bio: z.string().max(500).optional(),
  location: z.string().max(120).optional(),
  experience_years: z.coerce.number().min(0).max(50).optional().or(z.literal('')),
  skills: z.string().optional(),
})

type ProfileForm = z.infer<typeof profileSchema>

export function ProfileEditPage() {
  const navigate = useNavigate()
  const [avatar, setAvatar] = useState<File | null>(null)
  const [isSearchable, setIsSearchable] = useState(true)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: profileApi.getProfile,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
  })

  useEffect(() => {
    if (profile) {
      reset({
        first_name: profile.first_name,
        last_name: profile.last_name,
        university: profile.university,
        department: profile.department,
        bio: profile.bio,
        location: profile.location,
        experience_years: profile.experience_years,
        skills: profile.skills.map((s) => s.name).join(', '),
      })
      setIsSearchable(profile.is_searchable)
    }
  }, [profile, reset])

  const save = useMutation({
    mutationFn: (values: ProfileForm) => {
      const payload: ProfileInput = {
        first_name: values.first_name ?? undefined,
        last_name: values.last_name ?? undefined,
        university: values.university ?? undefined,
        department: values.department ?? undefined,
        bio: values.bio ?? undefined,
        location: values.location ?? undefined,
        experience_years:
          values.experience_years === '' ? undefined : Number(values.experience_years),
        skills: (values.skills ?? '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        is_searchable: isSearchable,
      }
      if (avatar) payload.avatar = avatar
      return profile ? profileApi.updateProfile(payload) : profileApi.createProfile(payload)
    },
    onSuccess: () => {
      navigate('/profile')
    },
    onError: (error) => setSubmitError(getErrorMessage(error)),
  })

  if (isLoading) return <LoadingState />
  if (isError) return <ErrorState message="Could not load your profile." />

  const onSubmit = handleSubmit((values) => save.mutate(values))

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-semibold text-gray-900">Edit profile</h1>
      <p className="mt-1 text-sm text-gray-500">
        Details on this page are shown on your public profile.
      </p>

      {submitError && (
        <div className="mt-4">
          <Alert variant="error">{submitError}</Alert>
        </div>
      )}

      <form onSubmit={onSubmit} className="mt-6 space-y-5 noValidate">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="First name" error={errors.first_name?.message}>
            <Input {...register('first_name')} />
          </Field>
          <Field label="Last name" error={errors.last_name?.message}>
            <Input {...register('last_name')} />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="University" error={errors.university?.message}>
            <Input placeholder="e.g. City University" {...register('university')} />
          </Field>
          <Field label="Department" error={errors.department?.message}>
            <Input placeholder="e.g. Computer Science" {...register('department')} />
          </Field>
        </div>

        <Field label="Bio" error={errors.bio?.message}>
          <Textarea rows={4} placeholder="Tell students about yourself…" {...register('bio')} />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Location" error={errors.location?.message}>
            <Input placeholder="e.g. Main campus" {...register('location')} />
          </Field>
          <Field
            label="Experience (years)"
            error={errors.experience_years?.message}
          >
            <Input type="number" min="0" max="100" {...register('experience_years')} />
          </Field>
        </div>

        <Field label="Skills (comma separated)">
          <Input placeholder="Python, Teaching, Web development" {...register('skills')} />
        </Field>

        <Field>
          <label
            className={classNames(
              'flex w-full cursor-pointer items-center justify-between rounded-md border border-dashed border-gray-300 px-4 py-3 text-sm text-gray-500 hover:border-primary-400',
            )}
          >
            <span>{avatar ? avatar.name : 'Upload a profile picture'}</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              className="sr-only"
              onChange={(e) => setAvatar(e.target.files?.[0] ?? null)}
            />
          </label>
        </Field>

        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={isSearchable}
            onChange={(e) => setIsSearchable(e.target.checked)}
          />
          Let students find me in searches
        </label>

        <div className="flex items-center gap-3">
          <Button type="submit" loading={isSubmitting || save.isPending}>
            Save profile
          </Button>
          <Button type="button" variant="ghost" onClick={() => navigate('/profile')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}