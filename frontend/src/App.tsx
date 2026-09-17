import { useState } from 'react'
import { fetchUsers } from './api/users'
import { FeedbackMessage } from './components/FeedbackMessage'
import { UserLookupForm } from './components/UserLookupForm'
import { UserResults } from './components/UserResults'
import type { UserFetchResponse } from './types/user'

export default function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<UserFetchResponse | null>(null)
  const [requestError, setRequestError] = useState<string | null>(null)

  async function handleLookup(userIds: number[]) {
    setRequestError(null)
    setResult(null)
    setIsLoading(true)

    try {
      const response = await fetchUsers(userIds)
      setResult(response)
    } catch (error) {
      setRequestError(
        error instanceof Error
          ? error.message
          : 'Ocorreu um erro inesperado. Tente novamente.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main>
      <div className="app-shell">
        <header className="page-header">
          <p className="eyebrow">
            Hit Digital <span aria-hidden="true">·</span> Full Stack Challenge
          </p>
          <h1>Consulta de usuários</h1>
          <p className="page-header__description">
            Informe os identificadores para consultar os usuários no provedor externo.
          </p>
        </header>

        <UserLookupForm isLoading={isLoading} onSubmit={handleLookup} />

        <div className="async-feedback" aria-live="polite" aria-atomic="true">
          {isLoading && <span className="sr-only">Consulta em andamento.</span>}
          {requestError && <FeedbackMessage message={requestError} />}
        </div>

        <div className="results-region" aria-live="polite" aria-atomic="true">
          {result && !requestError && (
            <UserResults users={result.users} failedIds={result.failed} />
          )}
        </div>
      </div>
    </main>
  )
}
