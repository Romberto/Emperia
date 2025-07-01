export interface TelegramAuthPayload {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
}


export interface TelegramAuthPayload {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

export interface GetCurrentUser {
  
    username:string;
    last_name?:string;
    id: string;
    first_name?: string;
    telegram_id: number;
    photo_url?: string;

}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  
}
