import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { Button } from '@/components/common/Button'
import { Alert } from '@/components/common/Feedback'
import { Field, Input } from '@/components/common/Field'
import { useAuth } from '@/hooks/useAuth'
import { getErrorMessage } from '@/api/client'

const loginSchema = z.object({
  identifier: z.string().min(1, 'Enter your email or username.'),
  password: z.string().min(1, 'Enter your password.'),
})

type LoginForm = z.infer<typeof loginSchema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const from =
    (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/'

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await login(values.identifier, values.password)
      navigate(from, { replace: true })
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <div className="mx-auto max-w-md py-12">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Log in to SkillSwap</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome back. Enter your email or username to continue.
        </p>

        {submitError && (
          <div className="mt-4">
            <Alert variant="error">{submitError}</Alert>
          </div>
        )}

        <form onSubmit={onSubmit} className="mt-5 space-y-4 noValidate">
          <Field label="Email or username" error={errors.identifier?.message}>
            <Input
              type="text"
              autoComplete="username"
              placeholder="you@university.edu"
              invalid={Boolean(errors.identifier)}
              {...register('identifier')}
            />
          </Field>

          <Field label="Password" error={errors.password?.message}>
            <Input
              type="password"
              autoComplete="current-password"
              invalid={Boolean(errors.password)}
              {...register('password')}
            />
          </Field>

          <div className="flex items-center justify-between text-sm">
            <Link
              to="/forgot-password"
              className="font-medium text-primary-600 hover:text-primary-700"
            >
              Forgot password?
            </Link>
          </div>

          <Button type="submit" loading={isSubmitting} className="w-full">
            Log in
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          Don&rsquo;t have an account?{' '}
          <Link
            to="/register"
            className="font-medium text-primary-600 hover:text-primary-700"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}