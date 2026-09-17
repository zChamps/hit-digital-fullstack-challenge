import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { fetchUsers } from './api/users'

vi.mock('./api/users', () => ({
  fetchUsers: vi.fn(),
}))

const mockedFetchUsers = vi.mocked(fetchUsers)

describe('App', () => {
  beforeEach(() => {
    mockedFetchUsers.mockReset()
  })

  it('renders returned users and failed IDs after submission', async () => {
    mockedFetchUsers.mockResolvedValue({
      users: [{ id: 1, name: 'Leanne Graham' }],
      failed: [3, 4],
    })
    const user = userEvent.setup()

    render(<App />)

    await user.type(screen.getByLabelText('IDs dos usuários'), '1, 3, 4')
    await user.click(screen.getByRole('button', { name: 'Consultar usuários' }))

    expect(mockedFetchUsers).toHaveBeenCalledWith([1, 3, 4])
    const returnedUser = await screen.findByText('Leanne Graham')
    expect(returnedUser).toBeInTheDocument()
    expect(returnedUser.closest('[aria-live="polite"]')).toHaveAttribute(
      'aria-atomic',
      'true',
    )
    expect(screen.getByText(/Não foi possível consultar os IDs: 3, 4/)).toBeInTheDocument()
  })
})
