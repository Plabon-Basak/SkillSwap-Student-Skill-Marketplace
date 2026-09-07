import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { getErrorMessage } from '@/api/client'
import { Button } from '@/components/common/Button'
import { Alert } from '@/components/common/Feedback'
import { Field, Input } from '@/components/common/Field'
import { useAuth } from '@/hooks/useAuth'
import { authService } from '@/services/auth'

const schema = z.object({
  code: z
    .string()
    .length(6, 'The verification code is 6 digits long.')
    .regex(/^\d{6}$/, 'The code contains only digits.'),
})

type Form = z.infer<typeof schema>

export function EmailVerificationPage() {
  const { user, refetchUser } = useAuth()
  const navigate = useNavigate()
  const [info, setInfo] = useState<string | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) })

  const requestCode = async () => {
    setInfo(null)
    setSubmitError(null)
    try {
      await authService.requestEmailVerification()
      setInfo('A verification code has been emailed to you.')
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  }

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await authService.verifyEmail(values.code)
      await refetchUser()
      navigate('/', { replace: true })
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <div className="mx-auto max-w-md py-12">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">Verify your email</h1>
        <p className="mt-1 text-sm text-gray-500">
          We sent a 6-digit code to{' '}
          <span className="font-medium text-gray-700">{user?.email}</span>. Enter it
          below to unlock the marketplace.
        </p>

        {info && (
          <div className="mt-4">
            <Alert variant="success">{info}</Alert>
          </div>
        )}
        {submitError && (
          <div className="mt-4">
            <Alert variant="error">{submitError}</Alert>
          </div>
        )}

        <form onSubmit={onSubmit} className="mt-5 space-y-4 noValidate">
          <Field label="Verification code" error={errors.code?.message}>
            <Input
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="123456"
              invalid={Boolean(errors.code)}
              {...register('code')}
            />
          </Field>
          <Button type="submit" loading={isSubmitting} className="w-full">
            Verify email
          </Button>
        </form>

        <button
          type="button"
          onClick={requestCode}
          className="mt-4 w-full text-center text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          Didn&rsquo;t receive it? Send a new code
        </button>
      </div>
    </div>
  )
}