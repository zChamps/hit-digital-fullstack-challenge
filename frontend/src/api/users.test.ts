import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchUsers, UserApiError } from './users'

const INVALID_RESPONSE_MESSAGE = 'O servidor retornou uma resposta inválida. Tente novamente.'

function mockSuccessfulResponse(body: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(body),
    }),
  )
}

describe('fetchUsers', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns a valid successful response', async () => {
    const response = {
      users: [{ id: 1, name: 'Leanne Graham' }],
      failed: [2],
    }
    mockSuccessfulResponse(response)

    await expect(fetchUsers([1, 2])).resolves.toEqual(response)
  })

  it.each([
    { users: {}, failed: [] },
    { users: [], failed: {} },
    { users: [{ id: '1', name: 'Leanne Graham' }], failed: [] },
    { users: [{ id: 1, name: 42 }], failed: [] },
    { users: [], failed: ['2'] },
  ])('rejects an invalid successful response: %j', async (body) => {
    mockSuccessfulResponse(body)

    await expect(fetchUsers([1])).rejects.toEqual(
      new UserApiError(INVALID_RESPONSE_MESSAGE),
    )
  })
})
