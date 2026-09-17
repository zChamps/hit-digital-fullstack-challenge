import { describe, expect, it } from 'vitest'
import { parseUserIds, UserIdValidationError } from './parseUserIds'

describe('parseUserIds', () => {
  it('parses comma, space and line-break separators', () => {
    expect(parseUserIds('1, 2 3\n4')).toEqual([1, 2, 3, 4])
  })

  it('preserves input order and duplicated IDs', () => {
    expect(parseUserIds('3, 1, 3, 2')).toEqual([3, 1, 3, 2])
  })

  it.each(['', '1, zero, 2', '1, 0, 2', '1, -2', '1,,2', '1.5, 2'])(
    'rejects invalid input: %j',
    (value) => {
      expect(() => parseUserIds(value)).toThrow(UserIdValidationError)
    },
  )
})
