import { fetchApiJson, patchApiJson, deleteApiJson } from "@/lib/api";
import { UserResponse, UserUpdate, ProfileResponse, ProfileUpdate } from "@/lib/profile";

export interface ListingsResponse {
  count: number;
  limit: number;
  offset: number;
  results: Array<{
    id: number;
    title: string;
    description: string;
    price: number;
    college: number;
    location_text: string;
    location: string;
    room_type: string;
    sqft: number;
    start_date: string | null;
    end_date: string | null;
    thumbnail_url: string | null;
    image_urls: string[];
    latitude: number | null;
    longitude: number | null;
    created_at: string | null;
  }>;
}

export const profileService = {
  // GET /users/me
  getMe: (token: string): Promise<UserResponse> =>
    fetchApiJson("/api/v1/users/me", token),

  // PATCH /users/me — email and username only
  updateMe: (token: string, payload: UserUpdate): Promise<UserResponse> =>
    patchApiJson("/api/v1/users/me", token, payload),

  // DELETE /users/me
  deleteMe: (token: string): Promise<void> =>
    deleteApiJson("/api/v1/users/me", token),

  // GET /profiles/me (adjust path to match your router)
  getMyProfile: (token: string): Promise<ProfileResponse> =>
    fetchApiJson("/api/v1/profiles/me", token),

  // PATCH /profiles/me
  updateMyProfile: (token: string, payload: ProfileUpdate): Promise<ProfileResponse> =>
    patchApiJson("/api/v1/profiles/me", token, payload),

  // GET /profiles/{username} — public profile
  getPublicProfile: (username: string): Promise<ProfileResponse> =>
    fetchApiJson(`/api/v1/profiles/${username}`),

  // GET /users/{user_id} — public user info
  getPublicUser: (userId: number): Promise<UserResponse> =>
    fetchApiJson(`/api/v1/users/${userId}`),

  // GET /listings/?host_id={user_id} — user's listings
  getUserListings: (userId: number, limit: number = 100): Promise<ListingsResponse> =>
    fetchApiJson(`/api/v1/listings/?host_id=${userId}&limit=${limit}`),
};
