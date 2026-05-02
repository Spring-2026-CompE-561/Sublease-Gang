"use client";

import { useEffect, useState } from "react";

import { ACCESS_TOKEN_KEY } from "@/lib/api";

export const REFRESH_TOKEN_KEY = "refresh_token";

const AUTH_CHANGED_EVENT = "sublease:auth-changed";

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
