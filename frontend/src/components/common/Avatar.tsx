import { classNames } from '@/utils/format'

const API_URL = import.meta.env.VITE_API_URL
  ? new URL(import.meta.env.VITE_API_URL).origin
  : 'http://localhost:8000'

export function mediaUrl(path: string | null | undefined): string | null {
  if (!path) return null
  if (path.startsWith('http'))
    return path
  return `${API_URL}${path}`
}

export function Avatar({
  src,
  name,
  size = 'md',
  className,
}: {
  src?: string | null
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}) {
  const sizes = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-16 w-16 text-xl',
    xl: 'h-20 w-20 text-2xl',
  }
  const resolved = mediaUrl(src)
  const initials = (name ?? '?')
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <span
      className={classNames(
        'inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary-100 font-medium text-primary-700',
        sizes[size],
        className,
      )}
      aria-hidden={!resolved}
    >
      {resolved ? (
        <img src={resolved} alt="" className="h-full w-full object-cover" />
      ) : (
        <span>{initials}</span>
      )}
    </span>
  )
}