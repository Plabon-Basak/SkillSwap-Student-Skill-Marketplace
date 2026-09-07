import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Badge, statusColor } from './Feedback'

describe('Badge', () => {
  it('renders its children', () => {
    render(<Badge>pending</Badge>)
    expect(screen.getByText('pending')).toBeInTheDocument()
  })
})

describe('statusColor', () => {
  it('maps statuses to badge colors', () => {
    expect(statusColor('completed')).toBe('green')
    expect(statusColor('pending')).toBe('amber')
    expect(statusColor('suspended')).toBe('red')
    expect(statusColor('unknown_status')).toBe('blue')
  })
})