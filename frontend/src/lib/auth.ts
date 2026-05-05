"use client";

import { useEffect, useState } from "react";

import { ACCESS_TOKEN_KEY, API_BASE_URL } from "@/lib/api";

export const REFRESH_TOKEN_KEY = "refresh_token";

export const AUTH_CHANGED_EVENT = "sublease:auth-changed";
export const AUTH_EXPIRED_EVENT = "sublease:auth-expired";

export interface AuthTokens {
	access_token: string;
	refresh_token?: string;
}

export function saveTokens(tokens: AuthTokens): void {
	if (typeof window === "undefined") {
		return;
	}
	localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
	if (tokens.refresh_token) {
		localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
	} else {
		localStorage.removeItem(REFRESH_TOKEN_KEY);
	}
	window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function clearTokens(): void {
	if (typeof window === "undefined") {
		return;
	}
	localStorage.removeItem(ACCESS_TOKEN_KEY);
	localStorage.removeItem(REFRESH_TOKEN_KEY);
	window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function getAccessToken(): string | null {
	if (typeof window === "undefined") {
		return null;
	}
	return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
	if (typeof window === "undefined") {
		return null;
	}
	return localStorage.getItem(REFRESH_TOKEN_KEY);
}

let refreshInFlight: Promise<string | null> | null = null;

export function refreshAccessToken(): Promise<string | null> {
	if (refreshInFlight) {
		return refreshInFlight;
	}

	const token = getRefreshToken();
	if (!token) {
		return Promise.resolve(null);
	}

	refreshInFlight = (async () => {
		try {
			const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ refresh_token: token }),
			});
			if (!res.ok) {
				return null;
			}
			const data = (await res.json()) as {
				access_token?: string;
				refresh_token?: string;
			};
			if (!data.access_token) {
				return null;
			}
			saveTokens({
				access_token: data.access_token,
				refresh_token: data.refresh_token,
			});
			return data.access_token;
		} catch {
			return null;
		} finally {
			refreshInFlight = null;
		}
	})();

	return refreshInFlight;
}

export function notifyAuthExpired(): void {
	if (typeof window === "undefined") {
		return;
	}
	window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
}

/**
 * User-initiated sign out. Tells the backend to revoke this session's
 * refresh token, then clears local storage. Best-effort: a failed
 * server call (network down, etc.) does not block the local logout.
 */
export async function signOut(): Promise<void> {
	if (typeof window === "undefined") {
		return;
	}
	const accessToken = getAccessToken();
	const refreshToken = getRefreshToken();
	if (accessToken) {
		try {
			await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${accessToken}`,
				},
				body: JSON.stringify(refreshToken ? { refresh_token: refreshToken } : {}),
			});
		} catch {
			// Network / server unavailable — fall through to local cleanup.
		}
	}
	clearTokens();
}

export function useIsAuthenticated(): boolean {
	const [isAuthed, setIsAuthed] = useState(false);

	useEffect(() => {
		const sync = () => setIsAuthed(Boolean(getAccessToken()));
		sync();

		const onStorage = (event: StorageEvent) => {
			if (event.key === ACCESS_TOKEN_KEY || event.key === null) {
				sync();
			}
		};

		window.addEventListener("storage", onStorage);
		window.addEventListener(AUTH_CHANGED_EVENT, sync);
		return () => {
			window.removeEventListener("storage", onStorage);
			window.removeEventListener(AUTH_CHANGED_EVENT, sync);
		};
	}, []);

	return isAuthed;
}
