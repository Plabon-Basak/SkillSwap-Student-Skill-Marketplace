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

const schema = z
  .object({
    email: z.string().email('Enter a valid email address.'),
    code: z
      .string()
      .length(6, 'The verification code is 6 digits long.')
      .regex(/^\d{6}$/, 'The code contains only digits.'),
    new_password: z
      .string()
      .min(8, 'Password must be at least 8 characters.')
      .max(128),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    path: ['confirm_password'],
    message: 'Passwords do not match.',
  })

type Form = z.infer<typeof schema>

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const [success, setSuccess] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) })

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await authService.resetPassword(
        values.email,
        values.code,
        values.new_password,
      )
      setSuccess('Password reset successfully. You can now log in.')
      setTimeout(() => navigate('/login'), 1500)
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <div className="mx-auto max-w-md py-12">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Choose a new password</h1>
        <p className="mt-1 text-sm text-gray-500">
          Enter the code emailed to you along with your new password.
        </p>

        {success && (
          <div className="mt-4">
            <Alert variant="success">{success}</Alert>
          </div>
        )}

        {!success && (
          <>
            {submitError && (
              <div className="mt-4">
                <Alert variant="error">{submitError}</Alert>
              </div>
            )}
            <form onSubmit={onSubmit} className="mt-5 space-y-4 noValidate">
              <Field label="Email" error={errors.email?.message}>
                <Input
                  type="email"
                  autoComplete="email"
                  invalid={Boolean(errors.email)}
                  {...register('email')}
                />
              </Field>
              <Field label="Reset code" error={errors.code?.message}>
                <Input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="123456"
                  invalid={Boolean(errors.code)}
                  {...register('code')}
                />
              </Field>
              <Field
                label="New password"
                error={errors.new_password?.message}
                hint="At least 8 characters."
              >
                <Input
                  type="password"
                  autoComplete="new-password"
                  invalid={Boolean(errors.new_password)}
                  {...register('new_password')}
                />
              </Field>
              <Field label="Confirm new password" error={errors.confirm_password?.message}>
                <Input
                  type="password"
                  autoComplete="new-password"
                  invalid={Boolean(errors.confirm_password)}
                  {...register('confirm_password')}
                />
              </Field>
              <Button type="submit" loading={isSubmitting} className="w-full">
                Reset password
              </Button>
            </form>
          </>
        )}

        <p className="mt-4 text-center text-sm text-gray-600">
          <Link
            to="/login"
            className="font-medium text-primary-600 hover:text-primary-700"
          >
            Back to log in
          </Link>
        </p>
      </div>
    </div>
  )
}