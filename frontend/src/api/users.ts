import type { UserFetchResponse } from '../types/user'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

export class UserApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'UserApiError'
  }
}

function getApiBaseUrl(): string {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

function isPositiveSafeInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value > 0
}

function isUserFetchResponse(body: unknown): body is UserFetchResponse {
  if (!body || typeof body !== 'object') {
    return false
  }

  const responseBody = body as Record<string, unknown>

  return (
    Array.isArray(responseBody.users) &&
    responseBody.users.every(
      (user) =>
        user !== null &&
        typeof user === 'object' &&
        isPositiveSafeInteger((user as Record<string, unknown>).id) &&
        typeof (user as Record<string, unknown>).name === 'string',
    ) &&
    Array.isArray(responseBody.failed) &&
    responseBody.failed.every(isPositiveSafeInteger)
  )
}

function getBackendMessage(body: unknown): string | null {
  if (!body || typeof body !== 'object') {
    return null
  }

  const responseBody = body as Record<string, unknown>

  if (typeof responseBody.message === 'string') {
    return responseBody.message
  }

  if (typeof responseBody.detail === 'string') {
    return responseBody.detail
  }

  if (Array.isArray(responseBody.detail)) {
    const firstDetail = responseBody.detail[0]
    if (firstDetail && typeof firstDetail === 'object') {
      const detailMessage = (firstDetail as Record<string, unknown>).msg
      return typeof detailMessage === 'string' ? detailMessage : null
    }
  }

  return null
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json()
    return getBackendMessage(body) ?? 'Não foi possível concluir a consulta.'
  } catch {
    return 'Não foi possível concluir a consulta.'
  }
}

export async function fetchUsers(userIds: number[]): Promise<UserFetchResponse> {
  let response: Response

  try {
    response = await fetch(`${getApiBaseUrl()}/api/users/fetch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_ids: userIds }),
    })
  } catch {
    throw new UserApiError(
      'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.',
    )
  }

  if (!response.ok) {
    throw new UserApiError(await getErrorMessage(response))
  }

  let body: unknown

  try {
    body = await response.json()
  } catch {
    throw new UserApiError('O servidor retornou uma resposta inválida. Tente novamente.')
  }

  if (!isUserFetchResponse(body)) {
    throw new UserApiError('O servidor retornou uma resposta inválida. Tente novamente.')
  }

  return body
}
