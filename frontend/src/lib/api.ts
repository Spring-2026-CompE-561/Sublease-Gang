export const API_BASE_URL = "http://localhost:8000";
export const ACCESS_TOKEN_KEY = "access_token";


export class ApiUnauthorizedError extends Error {
	constructor(message = "Your session expired. Please sign in again.") {
		super(message);
		this.name = "ApiUnauthorizedError";
	}
}


export function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function readApiErrorMessage(response: Response): Promise<string | null> {
	try {
		const payload = (await response.json()) as unknown;

		if (!isRecord(payload)) {
			return null;
		}

		if (Array.isArray(payload.detail)) {
			const detailMessages = payload.detail
				.map((entry) => {
					if (!isRecord(entry)) {
						return null;
					}

					const location = Array.isArray(entry.loc)
						? entry.loc.join(" > ")
						: null;
					const message =
						typeof entry.msg === "string" && entry.msg.trim().length > 0
							? entry.msg
							: null;

					if (!message) {
						return null;
					}

					return location ? `${location}: ${message}` : message;
				})
				.filter((entry): entry is string => entry !== null);

			if (detailMessages.length > 0) {
				return detailMessages.join("; ");
			}
		}

		const messageCandidates = [payload.detail, payload.message, payload.error];

		for (const candidate of messageCandidates) {
			if (typeof candidate === "string" && candidate.trim().length > 0) {
				return candidate;
			}
		}
	} catch {
		return null;
	}

	return null;
}


export async function fetchApiJson<T>(
	path: string,
	accessToken: string,
): Promise<T> {
	const response = await fetch(`${API_BASE_URL}${path}`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${accessToken}`,
		},
	});

	if (response.status === 401) {
		throw new ApiUnauthorizedError();
	}

	if (!response.ok) {
		const apiErrorMessage = await readApiErrorMessage(response);
		const errorSuffix = apiErrorMessage ? ` - ${apiErrorMessage}` : "";
		throw new Error(
			`Failed to load ${path}: ${response.status} ${response.statusText}${errorSuffix}`,
		);
	}

	return (await response.json()) as T;
}


export async function fetchApiJsonWithFallback<T>(
	paths: readonly string[],
	accessToken: string,
): Promise<T> {
	let lastError: Error | null = null;

	for (const path of paths) {
		try {
			return await fetchApiJson<T>(path, accessToken);
		} catch (error) {
			if (error instanceof ApiUnauthorizedError) {
				throw error;
			}

			const message = error instanceof Error ? error.message : String(error);
			const shouldRetry =
				message.includes(": 404 ") ||
				message.includes(": 405 ") ||
				message.includes(": 422 ");

			if (!shouldRetry) {
				throw error;
			}

			lastError = error instanceof Error ? error : new Error(message);
		}
	}

	throw (
		lastError ?? new Error("Failed to load data from all fallback endpoints.")
	);
}


export function isMissingDashboardEndpointError(error: unknown): boolean {
	if (!(error instanceof Error)) {
		return false;
	}

	return (
		error.message.includes(": 404 ") ||
		error.message.includes(": 405 ") ||
		error.message.includes(": 422 ")
	);
}


export async function postApiJsonWithFallback<TResponse, TBody>(
	paths: readonly string[],
	accessToken: string,
	body: TBody,
): Promise<TResponse> {
	let lastError: Error | null = null;

	for (const path of paths) {
		const response = await fetch(`${API_BASE_URL}${path}`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${accessToken}`,
			},
			body: JSON.stringify(body),
		});

		if (response.status === 401) {
			throw new ApiUnauthorizedError();
		}

		if (response.ok) {
			return (await response.json()) as TResponse;
		}

		const apiErrorMessage = await readApiErrorMessage(response);
		const errorSuffix = apiErrorMessage ? ` - ${apiErrorMessage}` : "";
		const error = new Error(
			`Failed to save to ${path}: ${response.status} ${response.statusText}${errorSuffix}`,
		);
		const shouldRetry = response.status === 404 || response.status === 405;

		if (!shouldRetry) {
			throw error;
		}

		lastError = error;
	}

	throw (
		lastError ?? new Error("Failed to save data to all fallback endpoints.")
	);
}

//this file is used from the professors repo 