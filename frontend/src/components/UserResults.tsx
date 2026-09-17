import type { User } from '../types/user'
import { FeedbackMessage } from './FeedbackMessage'

interface UserResultsProps {
  users: User[]
  failedIds: number[]
}

export function UserResults({ users, failedIds }: UserResultsProps) {
  const userCountLabel =
    users.length === 1 ? '1 usuário encontrado' : `${users.length} usuários encontrados`

  return (
    <section className="results" aria-labelledby="results-title">
      <div className="results__header">
        <div>
          <p className="section-label">Resultado</p>
          <h2 id="results-title">{userCountLabel}</h2>
        </div>
        <span className="results__status">Consulta concluída</span>
      </div>

      {users.length > 0 ? (
        <ul className="user-list" aria-label="Usuários encontrados">
          {users.map((user, index) => (
            <li className="user-card" key={`${user.id}-${index}`}>
              <div className="user-card__avatar" aria-hidden="true">
                {user.name.trim().charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="user-card__details">
                <span className="user-card__id">ID {user.id}</span>
                <strong>{user.name}</strong>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="results__empty">Nenhum usuário foi retornado nesta consulta.</p>
      )}

      {failedIds.length > 0 && (
        <div className="failed-results">
          <FeedbackMessage
            variant="warning"
            message={`${failedIds.length === 1 ? 'Não foi possível consultar o ID' : 'Não foi possível consultar os IDs'}: ${failedIds.join(', ')}.`}
          />
        </div>
      )}
    </section>
  )
}
