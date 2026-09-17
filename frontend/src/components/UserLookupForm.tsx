import { useState, type FormEvent } from 'react'
import { FeedbackMessage } from './FeedbackMessage'
import { parseUserIds, UserIdValidationError } from '../utils/parseUserIds'

interface UserLookupFormProps {
  isLoading: boolean
  onSubmit: (userIds: number[]) => Promise<void>
}

export function UserLookupForm({ isLoading, onSubmit }: UserLookupFormProps) {
  const [inputValue, setInputValue] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    let userIds: number[]

    try {
      userIds = parseUserIds(inputValue)
    } catch (error) {
      if (error instanceof UserIdValidationError) {
        setValidationError(error.message)
        return
      }

      throw error
    }

    setValidationError(null)
    await onSubmit(userIds)
  }

  return (
    <section className="lookup-panel" aria-labelledby="lookup-title">
      <div className="lookup-panel__heading">
        <div>
          <p className="section-label">Nova consulta</p>
          <h2 id="lookup-title">Quais usuários você procura?</h2>
        </div>
        <span className="lookup-panel__step" aria-hidden="true">01</span>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="user-ids">IDs dos usuários</label>
          <p id="user-ids-hint" className="field__hint">
            Separe os IDs com vírgulas, espaços ou quebras de linha.
          </p>
          <textarea
            id="user-ids"
            name="userIds"
            rows={4}
            value={inputValue}
            onChange={(event) => {
              setInputValue(event.target.value)
              if (validationError) setValidationError(null)
            }}
            placeholder="1, 2, 3, 4"
            aria-describedby={`user-ids-hint${validationError ? ' user-ids-error' : ''}`}
            aria-invalid={Boolean(validationError)}
            disabled={isLoading}
          />
        </div>

        {validationError && (
          <div id="user-ids-error">
            <FeedbackMessage message={validationError} />
          </div>
        )}

        <div className="form-actions">
          <p className="form-actions__note">A ordem e as duplicatas serão mantidas.</p>
          <button type="submit" disabled={isLoading}>
            {isLoading && <span className="spinner" aria-hidden="true" />}
            {isLoading ? 'Consultando...' : 'Consultar usuários'}
          </button>
        </div>
      </form>
    </section>
  )
}
