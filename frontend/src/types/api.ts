// Separate types file to avoid module resolution issues
export interface UserResponse {
  netid: string;
  name: string;
  email: string;
  majors: string[];
  minors?: string[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

