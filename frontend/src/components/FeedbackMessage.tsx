interface FeedbackMessageProps {
  message: string
  variant?: 'error' | 'warning'
}

export function FeedbackMessage({
  message,
  variant = 'error',
}: FeedbackMessageProps) {
  return (
    <div className={`feedback feedback--${variant}`} role="alert">
      <span className="feedback__symbol" aria-hidden="true">
        {variant === 'error' ? '!' : 'i'}
      </span>
      <p>{message}</p>
    </div>
  )
}
