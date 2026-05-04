import { fetchApiJson, patchApiJson } from "@/lib/api";
import { UserResponse, UserUpdate, ProfileResponse, ProfileUpdate } from "@/lib/profile";

export const profileService = {
  // GET /users/me
  getMe: (token: string): Promise<UserResponse> =>
    fetchApiJson("/api/v1/users/me", token),

  // PATCH /users/me — email and username only
  updateMe: (token: string, payload: UserUpdate): Promise<UserResponse> =>
    patchApiJson("/api/v1/users/me", token, payload),

  // GET /profiles/me (adjust path to match your router)
  getMyProfile: (token: string): Promise<ProfileResponse> =>
    fetchApiJson("/api/v1/profiles/me", token),

  // PATCH /profiles/me
  updateMyProfile: (token: string, payload: ProfileUpdate): Promise<ProfileResponse> =>
    patchApiJson("/api/v1/profiles/me", token, payload),
};
