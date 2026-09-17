const INVALID_INPUT_MESSAGE =
  'Informe apenas números inteiros positivos, separados por vírgulas, espaços ou linhas.'

export class UserIdValidationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'UserIdValidationError'
  }
}

export function parseUserIds(value: string): number[] {
  const normalizedValue = value.trim()

  if (!normalizedValue) {
    throw new UserIdValidationError('Informe pelo menos um ID para continuar.')
  }

  const hasEmptyCommaValue =
    /^,/.test(normalizedValue) ||
    /,$/.test(normalizedValue) ||
    /,\s*,/.test(normalizedValue)

  if (!/^[\d\s,]+$/.test(normalizedValue) || hasEmptyCommaValue) {
    throw new UserIdValidationError(INVALID_INPUT_MESSAGE)
  }

  const userIds = normalizedValue.split(/[,\s]+/).map(Number)

  if (userIds.some((id) => !Number.isSafeInteger(id) || id <= 0)) {
    throw new UserIdValidationError(INVALID_INPUT_MESSAGE)
  }

  return userIds
}
