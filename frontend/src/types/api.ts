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

export interface Schedule {
  id: number;
  netid: string;
  name: string;
  term: string;
  created: string;
  updated: string;
}

export interface ScheduleCourse {
  id: number;
  schedule_id: number;
  section_id: string;
  course_subject?: string;
  course_number?: string;
  course_title?: string;
  section_number?: string;
  meeting_days?: string[];
  start_end?: string[][]; // [[start, end], ...]
  instructors?: string[];
  color?: string; // Hex color code (e.g., "#3b82f6")
}

