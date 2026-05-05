import { API_BASE_URL } from "@/lib/api";

export interface PublicUser {
	id: number;
	email: string;
	username: string;
	account_disabled: boolean;
	created_at: string;
}

/** Public user lookup by id. SSR-friendly; returns null on missing/error. */
export async function fetchPublicUserById(
	userId: number,
): Promise<PublicUser | null> {
	if (!Number.isFinite(userId) || userId <= 0) return null;
	try {
		const init: RequestInit =
			typeof window === "undefined" ? { next: { revalidate: 60 } } : {};
		const res = await fetch(`${API_BASE_URL}/api/v1/users/${userId}`, init);
		if (res.ok) {
			return (await res.json()) as PublicUser;
		}
	} catch {
		// offline / SSR build without API
	}
	return null;
}
