export interface User {
  id: number
  name: string
}

export interface UserFetchResponse {
  users: User[]
  failed: number[]
}
