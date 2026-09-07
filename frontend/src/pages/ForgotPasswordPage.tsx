import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Button } from '@/components/common/Button'
import { Alert } from '@/components/common/Feedback'
import { Field, Input } from '@/components/common/Field'
import { authService } from '@/services/auth'

const schema = z.object({
  email: z.string().email('Enter a valid email address.'),
})

type Form = z.infer<typeof schema>

export function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) })

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await authService.requestPasswordReset(values.email)
      setSent(true)
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <div className="mx-auto max-w-md py-12">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Reset your password</h1>
        <p className="mt-1 text-sm text-gray-500">
          Enter your email and we&rsquo;ll send you a 6-digit reset code.
        </p>

        {sent && (
          <div className="mt-4">
            <Alert variant="success">
              If an account exists for that email, a reset code is on the way. Check
              your inbox, then continue to the reset page.
            </Alert>
            <Link
              to="/reset-password"
              className="mt-4 inline-block font-medium text-primary-600 hover:text-primary-700"
            >
              I have my code → Reset password
            </Link>
          </div>
        )}

        {!sent && (
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
              <Button type="submit" loading={isSubmitting} className="w-full">
                Send reset code
              </Button>
            </form>
          </>
        )}

        <p className="mt-4 text-center text-sm text-gray-600">
          Remembered it?{' '}
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