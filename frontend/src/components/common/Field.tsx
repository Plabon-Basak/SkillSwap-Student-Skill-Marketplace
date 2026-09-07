import { forwardRef, type InputHTMLAttributes } from 'react'

import { classNames } from '@/utils/format'

interface FieldWrapProps {
  label?: string
  error?: string
  hint?: string
  children: React.ReactNode
}

export function Field({ label, error, hint, children }: FieldWrapProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">{label}</label>
      )}
      {children}
      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : hint ? (
        <p className="text-sm text-gray-500">{hint}</p>
      ) : null}
    </div>
  )
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { invalid, className, ...rest },
  ref,
) {
  return (
    <input
      ref={ref}
      aria-invalid={invalid || undefined}
      className={classNames(
        'block w-full rounded-md border bg-white px-3 py-2 text-sm shadow-sm',
        'placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
        invalid ? 'border-red-500' : 'border-gray-300',
        className,
      )}
      {...rest}
    />
  )
})

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  function Textarea({ invalid, className, ...rest }, ref) {
    return (
      <textarea
        ref={ref}
        aria-invalid={invalid || undefined}
        className={classNames(
          'block w-full rounded-md border bg-white px-3 py-2 text-sm shadow-sm',
          'placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
          invalid ? 'border-red-500' : 'border-gray-300',
          className,
        )}
        {...rest}
      />
    )
  },
)

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { invalid, className, children, ...rest },
  ref,
) {
  return (
    <select
      ref={ref}
      className={classNames(
        'block w-full rounded-md border bg-white px-3 py-2 text-sm shadow-sm',
        'focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
        invalid ? 'border-red-500' : 'border-gray-300',
        className,
      )}
      {...rest}
    >
      {children}
    </select>
  )
})