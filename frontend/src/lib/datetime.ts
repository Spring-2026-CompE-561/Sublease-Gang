/**
 * API timestamps should be ISO-8601 with a timezone (e.g. "Z" or "+00:00").
 * If the backend returns a timezone-less ISO string, browsers may interpret it
 * as local time, causing incorrect message times. We normalize that case to UTC.
 */
export function parseApiDateTime(value: string): Date {
	// Fast-path: Date can already parse it (e.g. includes "Z" or an offset).
	const direct = new Date(value);
	if (!Number.isNaN(direct.getTime())) return direct;

	// Normalize common "YYYY-MM-DDTHH:mm:ss(.sss)" strings missing timezone to UTC.
	const looksLikeIso =
		/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/.test(value);
	if (looksLikeIso) {
		const normalized = new Date(`${value}Z`);
		if (!Number.isNaN(normalized.getTime())) return normalized;
	}

	// Last resort: return invalid date for callers to handle.
	return direct;
}

function isSameLocalDay(a: Date, b: Date): boolean {
	return (
		a.getFullYear() === b.getFullYear() &&
		a.getMonth() === b.getMonth() &&
		a.getDate() === b.getDate()
	);
}

/**
 * Friendly message timestamp formatting:
 * - Today: time only
 * - Same year: "MMM d, h:mm AM/PM"
 * - Different year: "MMM d, yyyy, h:mm AM/PM"
 */
export function formatMessageTimestamp(value: string, locale?: string): string {
	const date = parseApiDateTime(value);
	if (Number.isNaN(date.getTime())) return value;

	const now = new Date();
	const isToday = isSameLocalDay(date, now);

	if (isToday) {
		return new Intl.DateTimeFormat(locale, { timeStyle: "short" }).format(date);
	}

	const sameYear = date.getFullYear() === now.getFullYear();
	return new Intl.DateTimeFormat(locale, {
		dateStyle: sameYear ? "medium" : "long",
		timeStyle: "short",
	}).format(date);
}

