import { describe, expect, it } from 'vitest'

import { classNames, formatCurrency, titleCase, truncate } from './format'

describe('format helpers', () => {
  it('formats currency', () => {
    expect(formatCurrency('10.5')).toBe('$10.50')
    expect(formatCurrency(1234.5, 'USD')).toBe('$1,234.50')
  })

  it('falls back when the amount is not numeric', () => {
    expect(formatCurrency('abc', 'USD')).toBe('USD abc')
  })

  it('truncates long text', () => {
    expect(truncate('short')).toBe('short')
    expect(truncate('a'.repeat(200), 10).length).toBeLessThanOrEqual(10)
  })

  it('title-cases snake_case', () => {
    expect(titleCase('pending_payment')).toBe('Pending Payment')
  })

  it('joins class names, filtering falsy values', () => {
    expect(classNames('a', false, null, undefined, 'b')).toBe('a b')
  })
})