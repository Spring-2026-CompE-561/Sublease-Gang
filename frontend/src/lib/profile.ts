export interface UserResponse {
  id: number;
  email: string;
  username: string;
  account_disabled: boolean;
  created_at: string;
}

export interface UserUpdate {
  email?: string;
  username?: string;
}

export interface ProfileResponse {
  user_id: number;
  firstname: string;
  lastname: string;
  username: string;
  icon?: string;
  description?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface ProfileUpdate {
  firstname?: string;
  lastname?: string;
  username?: string;
  icon?: string;
  description?: string;
  contact_email?: string;
  contact_phone?: string;
}
