"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Loader2, MessageSquare } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ApiUnauthorizedError, fetchApiJson } from "@/lib/api";
import { clearTokens, getAccessToken } from "@/lib/auth";
import {
	fetchConversationMessages,
	fetchConversations,
	isApiUnauthorizedError,
	MESSAGES_PAGE_SIZE,
	sendConversationMessage,
} from "@/lib/conversations";
import type { Conversation, Message } from "@/types/conversation";
import { MESSAGE_CONTENT_MAX_LENGTH } from "@/types/conversation";
import { cn } from "@/lib/utils";

type MeResponse = { id: number; username: string };
type ListingTitleResponse = { id: number; title: string };

function parseConversationQuery(raw: string | null): number | null {
	if (!raw) return null;
	const n = Number.parseInt(raw, 10);
	return Number.isFinite(n) && n > 0 ? n : null;
}

function otherParticipantId(conversation: Conversation, meId: number): number {
	return conversation.user_one_id === meId
		? conversation.user_two_id
		: conversation.user_one_id;
}

export function MessagesView() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const conversationFromUrl = useMemo(
		() => parseConversationQuery(searchParams.get("conversation")),
		[searchParams],
	);

	const bottomAnchorRef = useRef<HTMLDivElement>(null);

	const [sessionReady, setSessionReady] = useState(false);
	const [sessionError, setSessionError] = useState<string | null>(null);
	const [meId, setMeId] = useState<number | null>(null);
	const [conversations, setConversations] = useState<Conversation[]>([]);
	const [conversationsLoading, setConversationsLoading] = useState(true);
	const [conversationsError, setConversationsError] = useState<string | null>(
		null,
	);

	const [selectedId, setSelectedId] = useState<number | null>(null);
	const [listingTitles, setListingTitles] = useState<Record<number, string>>(
		{},
	);

	const [messages, setMessages] = useState<Message[]>([]);
	const [messagesLoading, setMessagesLoading] = useState(false);
	const [messagesLoadingMore, setMessagesLoadingMore] = useState(false);
	const [messagesError, setMessagesError] = useState<string | null>(null);
	const [hasMoreMessages, setHasMoreMessages] = useState(false);

	const [draft, setDraft] = useState("");
	const [sendBusy, setSendBusy] = useState(false);

	const scrollToBottom = useCallback(() => {
		requestAnimationFrame(() => {
			bottomAnchorRef.current?.scrollIntoView({ behavior: "smooth" });
		});
	}, []);

	const handleUnauthorized = useCallback(() => {
		clearTokens();
		toast.error(new ApiUnauthorizedError().message);
		router.replace("/signin");
	}, [router]);

	const loadInitialData = useCallback(async () => {
		const token = getAccessToken();
		if (!token) {
			router.replace("/signin");
			return;
		}

		setConversationsLoading(true);
		setConversationsError(null);
		setSessionError(null);

		try {
			const me = await fetchApiJson<MeResponse>("/api/v1/users/me", token);
			setMeId(me.id);
			setSessionReady(true);
		} catch (error) {
			if (isApiUnauthorizedError(error)) {
				handleUnauthorized();
				return;
			}
			const message = error instanceof Error ? error.message : String(error);
			setSessionError(message);
			setConversationsLoading(false);
			return;
		}

		try {
			const list = await fetchConversations(token);
			setConversations(list);
		} catch (error) {
			if (isApiUnauthorizedError(error)) {
				handleUnauthorized();
				return;
			}
			const message = error instanceof Error ? error.message : String(error);
			setConversationsError(message);
		} finally {
			setConversationsLoading(false);
		}
	}, [handleUnauthorized, router]);

	/* eslint-disable react-hooks/set-state-in-effect -- mount / URL sync data loading */
	useEffect(() => {
		void loadInitialData();
	}, [loadInitialData]);

	// Sync selection from URL once conversations (or URL) are known.
	useEffect(() => {
		if (!sessionReady || meId === null) return;

		if (conversationFromUrl !== null) {
			setSelectedId(conversationFromUrl);
			return;
		}

		if (conversations.length > 0) {
			setSelectedId((prev) => prev ?? conversations[0].id);
		} else {
			setSelectedId(null);
		}
	}, [sessionReady, meId, conversationFromUrl, conversations]);

	const selectConversation = useCallback(
		(id: number) => {
			setSelectedId(id);
			const next = new URLSearchParams(searchParams.toString());
			next.set("conversation", String(id));
			router.replace(`/messages?${next.toString()}`, { scroll: false });
		},
		[router, searchParams],
	);

	const loadMessagesFirstPage = useCallback(
		async (conversationId: number) => {
			const token = getAccessToken();
			if (!token) {
				handleUnauthorized();
				return;
			}

			setMessagesLoading(true);
			setMessagesError(null);
			setMessages([]);
			setHasMoreMessages(false);

			try {
				const batch = await fetchConversationMessages(token, conversationId, {
					skip: 0,
					limit: MESSAGES_PAGE_SIZE,
				});
				setMessages(batch);
				setHasMoreMessages(batch.length === MESSAGES_PAGE_SIZE);
			} catch (error) {
				if (isApiUnauthorizedError(error)) {
					handleUnauthorized();
					return;
				}
				const message = error instanceof Error ? error.message : String(error);
				setMessagesError(message);
			} finally {
				setMessagesLoading(false);
			}
		},
		[handleUnauthorized],
	);

	useEffect(() => {
		if (selectedId === null) return;
		void loadMessagesFirstPage(selectedId);
	}, [selectedId, loadMessagesFirstPage]);

	useEffect(() => {
		if (conversations.length === 0) return;

		const missing = Array.from(
			new Set(
				conversations
					.map((c) => c.listing_id)
					.filter((id) => listingTitles[id] === undefined),
			),
		);
		if (missing.length === 0) return;

		const token = getAccessToken();
		if (!token) return;

		let cancelled = false;
		(async () => {
			const results = await Promise.all(
				missing.map(async (id) => {
					try {
						const data = await fetchApiJson<ListingTitleResponse>(
							`/api/v1/listings/${id}`,
							token,
						);
						return [id, data.title] as const;
					} catch {
						return null;
					}
				}),
			);
			if (cancelled) return;
			const additions = results.filter(
				(entry): entry is readonly [number, string] => entry !== null,
			);
			if (additions.length === 0) return;
			setListingTitles((prev) => {
				const next = { ...prev };
				for (const [id, title] of additions) {
					next[id] = title;
				}
				return next;
			});
		})();

		return () => {
			cancelled = true;
		};
	}, [conversations, listingTitles]);

	/* eslint-enable react-hooks/set-state-in-effect */

	useEffect(() => {
		if (messagesLoading || messages.length === 0) return;
		scrollToBottom();
	}, [messagesLoading, messages, scrollToBottom]);

	async function loadMoreMessages() {
		if (selectedId === null || messagesLoadingMore || !hasMoreMessages) return;
		const token = getAccessToken();
		if (!token) {
			handleUnauthorized();
			return;
		}

		setMessagesLoadingMore(true);
		setMessagesError(null);

		try {
			const batch = await fetchConversationMessages(token, selectedId, {
				skip: messages.length,
				limit: MESSAGES_PAGE_SIZE,
			});
			setMessages((prev) => [...prev, ...batch]);
			setHasMoreMessages(batch.length === MESSAGES_PAGE_SIZE);
		} catch (error) {
			if (isApiUnauthorizedError(error)) {
				handleUnauthorized();
				return;
			}
			const message = error instanceof Error ? error.message : String(error);
			setMessagesError(message);
		} finally {
			setMessagesLoadingMore(false);
		}
	}

	async function handleSend() {
		const trimmed = draft.trim();
		if (!trimmed || selectedId === null) return;

		if (trimmed.length > MESSAGE_CONTENT_MAX_LENGTH) {
			toast.error(
				`Message is too long (max ${MESSAGE_CONTENT_MAX_LENGTH} characters).`,
			);
			return;
		}

		const token = getAccessToken();
		if (!token) {
			handleUnauthorized();
			return;
		}

		setSendBusy(true);
		setMessagesError(null);

		try {
			const created = await sendConversationMessage(token, selectedId, trimmed);
			setDraft("");
			setMessages((prev) => {
				if (prev.some((m) => m.id === created.id)) {
					return prev;
				}
				return [...prev, created];
			});
		} catch (error) {
			if (isApiUnauthorizedError(error)) {
				handleUnauthorized();
				return;
			}
			const message = error instanceof Error ? error.message : String(error);
			setMessagesError(message);
			toast.error(message);
		} finally {
			setSendBusy(false);
		}
	}

	if (!sessionReady && conversationsLoading) {
		return (
			<main className="container mx-auto flex flex-1 items-center justify-center px-4 py-16">
				<p className="flex items-center gap-2 text-sm text-muted-foreground">
					<Loader2 className="size-4 animate-spin" aria-hidden />
					Loading messages…
				</p>
			</main>
		);
	}

	if (sessionError) {
		return (
			<main className="container mx-auto flex flex-1 flex-col items-center justify-center gap-4 px-4 py-16">
				<p className="max-w-md text-center text-sm text-destructive">{sessionError}</p>
				<Button type="button" variant="outline" onClick={() => void loadInitialData()}>
					Try again
				</Button>
			</main>
		);
	}

	if (!sessionReady) {
		return (
			<main className="container mx-auto flex-1 px-4 py-16 text-center">
				<p className="text-muted-foreground">Redirecting to sign in…</p>
			</main>
		);
	}

	const selected = conversations.find((c) => c.id === selectedId) ?? null;

	return (
		<main className="flex min-h-0 flex-1 flex-col">
			<div className="border-b bg-background">
				<div className="mx-auto max-w-6xl px-4 py-6 md:px-6">
					<h1 className="text-2xl font-semibold tracking-tight">Messages</h1>
					<p className="mt-1 text-sm text-muted-foreground">
						Chats about listings you&apos;re part of.
					</p>
				</div>
			</div>

			<div className="mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col gap-0 px-4 py-6 md:flex-row md:px-6 md:gap-4">
				<aside className="mb-4 flex max-h-48 shrink-0 flex-col rounded-xl border bg-card md:mb-0 md:max-h-none md:w-72 md:shrink-0">
					<div className="border-b px-3 py-2">
						<p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
							Conversations
						</p>
					</div>
					<div className="min-h-0 flex-1 overflow-y-auto p-2">
						{conversationsLoading ? (
							<p className="flex items-center gap-2 px-2 py-4 text-sm text-muted-foreground">
								<Loader2 className="size-4 shrink-0 animate-spin" aria-hidden />
								Loading…
							</p>
						) : conversationsError ? (
							<div className="space-y-2 px-2 py-3">
								<p className="text-sm text-destructive">{conversationsError}</p>
								<Button
									type="button"
									variant="outline"
									size="sm"
									className="w-full"
									onClick={() => void loadInitialData()}
								>
									Try again
								</Button>
							</div>
						) : conversations.length === 0 ? (
							<div className="flex flex-col items-center gap-2 px-2 py-8 text-center">
								<MessageSquare
									className="size-10 text-muted-foreground/60"
									aria-hidden
								/>
								<p className="text-sm text-muted-foreground">
									No conversations yet. Message a host from a listing to start
									one.
								</p>
								<Link
									href="/listings"
									className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
								>
									Browse listings
								</Link>
							</div>
						) : (
							<ul className="space-y-1">
								{conversations.map((c) => {
									const active = c.id === selectedId;
									const other =
										meId !== null ? otherParticipantId(c, meId) : c.user_two_id;
									return (
										<li key={c.id}>
											<button
												type="button"
												onClick={() => selectConversation(c.id)}
												className={`flex w-full flex-col rounded-lg px-3 py-2.5 text-left text-sm transition hover:bg-muted/80 ${
													active ? "bg-muted font-medium" : ""
												}`}
											>
												<span className="line-clamp-1">
													{listingTitles[c.listing_id] ??
														`Listing #${c.listing_id}`}
												</span>
												<span className="text-xs text-muted-foreground">
													with user #{other}
												</span>
											</button>
										</li>
									);
								})}
							</ul>
						)}
					</div>
				</aside>

				<section className="flex min-h-[420px] min-w-0 flex-1 flex-col rounded-xl border bg-card shadow-sm">
					{selectedId === null ? (
						<div className="flex flex-1 flex-col items-center justify-center gap-2 p-8 text-center text-muted-foreground">
							<MessageSquare className="size-10 opacity-50" aria-hidden />
							<p className="text-sm">Select a conversation to view messages.</p>
						</div>
					) : (
						<>
							<div className="border-b px-4 py-3">
								<h2 className="text-sm font-semibold">
									{selected
										? (listingTitles[selected.listing_id] ??
											`Listing #${selected.listing_id}`)
										: `Conversation #${selectedId}`}
								</h2>
								{selected && meId !== null ? (
									<p className="text-xs text-muted-foreground">
										with user #{otherParticipantId(selected, meId)}
									</p>
								) : null}
							</div>

							<div className="flex min-h-0 flex-1 flex-col">
								<div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-4">
									{messagesLoading ? (
										<p className="flex items-center gap-2 text-sm text-muted-foreground">
											<Loader2 className="size-4 animate-spin" aria-hidden />
											Loading thread…
										</p>
									) : messagesError ? (
										<div className="space-y-2">
											<p className="text-sm text-destructive">{messagesError}</p>
											<Button
												type="button"
												variant="outline"
												size="sm"
												onClick={() =>
													selectedId !== null &&
													void loadMessagesFirstPage(selectedId)
												}
											>
												Retry
											</Button>
										</div>
									) : messages.length === 0 ? (
										<p className="text-sm text-muted-foreground">
											No messages yet. Say hello below.
										</p>
									) : (
										<ul className="flex flex-col gap-2">
											{messages.map((m) => {
												const mine = meId !== null && m.sender_id === meId;
												return (
													<li
														key={m.id}
														className={`flex ${mine ? "justify-end" : "justify-start"}`}
													>
														<Card
															className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm shadow-none ${
																mine
																	? "bg-primary text-primary-foreground"
																	: "bg-muted"
															}`}
														>
															<p className="whitespace-pre-wrap wrap-break-word">
																{m.content}
															</p>
															<time
																className={`mt-1 block text-[10px] opacity-80 ${
																	mine ? "text-right" : ""
																}`}
																dateTime={m.created_at}
															>
																{new Date(m.created_at).toLocaleString(undefined, {
																	dateStyle: "short",
																	timeStyle: "short",
																})}
															</time>
														</Card>
													</li>
												);
											})}
											{hasMoreMessages ? (
												<li className="flex justify-center py-2">
													<Button
														type="button"
														variant="ghost"
														size="sm"
														disabled={messagesLoadingMore}
														onClick={() => void loadMoreMessages()}
													>
														{messagesLoadingMore ? (
															<>
																<Loader2
																	className="mr-2 size-4 animate-spin"
																	aria-hidden
																/>
																Loading…
															</>
														) : (
															"Load more messages"
														)}
													</Button>
												</li>
											) : null}
										</ul>
									)}
									<div ref={bottomAnchorRef} />
								</div>

								<div className="border-t p-3">
									<Textarea
										placeholder="Write a message…"
										rows={3}
										maxLength={MESSAGE_CONTENT_MAX_LENGTH}
										value={draft}
										disabled={sendBusy || messagesLoading}
										onChange={(e) => setDraft(e.target.value)}
										onKeyDown={(e) => {
											if (e.key === "Enter" && !e.shiftKey) {
												e.preventDefault();
												if (!sendBusy && draft.trim()) {
													void handleSend();
												}
											}
										}}
										className="resize-none bg-background"
									/>
									<div className="mt-2 flex items-center justify-between gap-2">
										<span className="text-[11px] text-muted-foreground">
											{draft.length}/{MESSAGE_CONTENT_MAX_LENGTH} · Enter to send,
											Shift+Enter for newline
										</span>
										<Button
											type="button"
											size="sm"
											disabled={
												sendBusy ||
												messagesLoading ||
												!draft.trim() ||
												selectedId === null
											}
											onClick={() => void handleSend()}
										>
											{sendBusy ? (
												<>
													<Loader2 className="mr-2 size-4 animate-spin" />
													Sending…
												</>
											) : (
												"Send"
											)}
										</Button>
									</div>
								</div>
							</div>
						</>
					)}
				</section>
			</div>
		</main>
	);
}
