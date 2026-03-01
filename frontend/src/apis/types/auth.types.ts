export interface User {
  id: string;
  username: string;
  email: string;
  password: string;
  is_active: boolean;
  created_at: string;
}

export type UserRegiser = Pick<User, 'username' | 'email' | 'password'>;
export type UserLogin = Pick<User, 'email' | 'password'>;
export type UserProfile = Omit<User, 'password'>;

export interface TokenResponse {
  access_token: string;
  token_type?: string;
  user: UserProfile;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordChangeResponse {
  message?: string;
  access_token: string;
  token_type?: string;
}
