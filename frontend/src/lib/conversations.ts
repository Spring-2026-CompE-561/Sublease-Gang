import {
	ApiUnauthorizedError,
	fetchApiJson,
	postApiJson,
} from "@/lib/api";
import type { Conversation, Message } from "@/types/conversation";

export const CONVERSATIONS_LIST_PATH = "/api/v1/conversations/" as const;
export const MESSAGES_PAGE_SIZE = 50;

export function conversationMessagesPath(conversationId: number): string {
	return `/api/v1/conversations/${conversationId}/messages`;
}

export async function fetchConversations(
	accessToken: string,
): Promise<Conversation[]> {
	return fetchApiJson<Conversation[]>(CONVERSATIONS_LIST_PATH, accessToken);
}

export async function fetchConversationMessages(
	accessToken: string,
	conversationId: number,
	options: { skip: number; limit?: number },
): Promise<Message[]> {
	const limit = options.limit ?? MESSAGES_PAGE_SIZE;
	const qs = new URLSearchParams({
		skip: String(options.skip),
		limit: String(limit),
	});
	return fetchApiJson<Message[]>(
		`${conversationMessagesPath(conversationId)}?${qs.toString()}`,
		accessToken,
	);
}

export async function sendConversationMessage(
	accessToken: string,
	conversationId: number,
	content: string,
): Promise<Message> {
	return postApiJson<Message, { content: string }>(
		conversationMessagesPath(conversationId),
		accessToken,
		{ content },
	);
}

export function isApiUnauthorizedError(
	error: unknown,
): error is ApiUnauthorizedError {
	return error instanceof ApiUnauthorizedError;
}
