/** Mirrors GET/POST `/api/v1/conversations/` */
export type Conversation = {
	id: number;
	listing_id: number;
	user_one_id: number;
	user_two_id: number;
	created_at: string;
};

/** Mirrors GET/POST `/api/v1/conversations/{id}/messages` */
export type Message = {
	id: number;
	conversation_id: number;
	sender_id: number;
	content: string;
	created_at: string;
};

export const MESSAGE_CONTENT_MAX_LENGTH = 5000;
