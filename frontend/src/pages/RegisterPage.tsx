import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Button } from '@/components/common/Button'
import { Alert } from '@/components/common/Feedback'
import { Field, Input } from '@/components/common/Field'
import { authService } from '@/services/auth'

const registerSchema = z
  .object({
    first_name: z.string().max(150).optional(),
    last_name: z.string().max(150).optional(),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters.')
      .max(30, 'Username must be at most 30 characters.')
      .regex(/^[\w.@+-]+$/, 'Username contains invalid characters.'),
    email: z.string().email('Enter a valid email address.'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters.')
      .max(128),
    confirm_password: z.string(),
  })
  .refine((data) => data.password === data.confirm_password, {
    path: ['confirm_password'],
    message: 'Passwords do not match.',
  })

type RegisterForm = z.infer<typeof registerSchema>

export function RegisterPage() {
  const navigate = useNavigate()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await authService.register({
        first_name: values.first_name || undefined,
        last_name: values.last_name || undefined,
        username: values.username,
        email: values.email,
        password: values.password,
      })
      navigate('/login', {
        state: { justRegistered: true },
        replace: true,
      })
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <div className="mx-auto max-w-md py-12">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Create your account</h1>
        <p className="mt-1 text-sm text-gray-500">
          Join SkillSwap and start trading skills with students.
        </p>

        {submitError && (
          <div className="mt-4">
            <Alert variant="error">{submitError}</Alert>
          </div>
        )}

        <form onSubmit={onSubmit} className="mt-5 space-y-4 noValidate">
          <Field label="First name" error={errors.first_name?.message}>
            <Input
              type="text"
              autoComplete="given-name"
              invalid={Boolean(errors.first_name)}
              {...register('first_name')}
            />
          </Field>

          <Field label="Last name" error={errors.last_name?.message}>
            <Input
              type="text"
              autoComplete="family-name"
              invalid={Boolean(errors.last_name)}
              {...register('last_name')}
            />
          </Field>

          <Field label="Username" error={errors.username?.message}>
            <Input
              type="text"
              autoComplete="username"
              invalid={Boolean(errors.username)}
              {...register('username')}
            />
          </Field>

          <Field label="Email" error={errors.email?.message}>
            <Input
              type="email"
              autoComplete="email"
              placeholder="you@university.edu"
              invalid={Boolean(errors.email)}
              {...register('email')}
            />
          </Field>

          <Field
            label="Password"
            error={errors.password?.message}
            hint="At least 8 characters, not too common."
          >
            <Input
              type="password"
              autoComplete="new-password"
              invalid={Boolean(errors.password)}
              {...register('password')}
            />
          </Field>

          <Field label="Confirm password" error={errors.confirm_password?.message}>
            <Input
              type="password"
              autoComplete="new-password"
              invalid={Boolean(errors.confirm_password)}
              {...register('confirm_password')}
            />
          </Field>

          <Button type="submit" loading={isSubmitting} className="w-full">
            Create account
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-medium text-primary-600 hover:text-primary-700"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}