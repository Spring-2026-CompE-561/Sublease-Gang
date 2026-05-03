"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { API_BASE_URL, ACCESS_TOKEN_KEY, readApiErrorMessage } from "@/lib/api";

type Conversation = {
	id: number;
	listing_id: number;
	user_one_id: number;
	user_two_id: number;
	created_at: string;
};

type Message = {
	id: number;
	conversation_id: number;
	sender_id: number;
	content: string;
	created_at: string;
};

type Me = {
	id: number;
	email: string;
	username: string;
};

export default function MessagesPage() {
	const [me, setMe] = useState<Me | null>(null);
	const [conversations, setConversations] = useState<Conversation[]>([]);
	const [activeId, setActiveId] = useState<number | null>(null);
	const [messages, setMessages] = useState<Message[]>([]);
	const [draft, setDraft] = useState("");
	const [loading, setLoading] = useState(true);
	const [sending, setSending] = useState(false);
	const [needsSignIn, setNeedsSignIn] = useState(false);

	const bottomRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		async function load() {
			const token = localStorage.getItem(ACCESS_TOKEN_KEY);
			if (!token) {
				setNeedsSignIn(true);
				setLoading(false);
				return;
			}

			const headers = { Authorization: `Bearer ${token}` };
			const meRes = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
				headers,
			});
			const convRes = await fetch(`${API_BASE_URL}/api/v1/conversations/`, {
				headers,
			});

			if (meRes.status === 401 || convRes.status === 401) {
				setNeedsSignIn(true);
				setLoading(false);
				return;
			}

			if (!meRes.ok || !convRes.ok) {
				toast.error("Could not load messages");
				setLoading(false);
				return;
			}

			const meData = (await meRes.json()) as Me;
			const convData = (await convRes.json()) as Conversation[];

			setMe(meData);
			setConversations(convData);
			if (convData.length > 0) {
				setActiveId(convData[0].id);
			}
			setLoading(false);
		}

		load();
	}, []);

	useEffect(() => {
		if (activeId == null) return;

		let cancelled = false;
		async function loadMsgs() {
			const token = localStorage.getItem(ACCESS_TOKEN_KEY);
			const res = await fetch(
				`${API_BASE_URL}/api/v1/conversations/${activeId}/messages`,
				{ headers: { Authorization: `Bearer ${token}` } },
			);
			if (cancelled) return;

			if (!res.ok) {
				console.error("loadMsgs failed", res.status);
				setMessages([]);
				return;
			}

			const data = (await res.json()) as Message[];
			setMessages(data);
		}

		loadMsgs();
		return () => {
			cancelled = true;
		};
	}, [activeId]);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages.length]);

	async function send() {
		const text = draft.trim();
		if (!text || activeId == null) return;

		setSending(true);
		const token = localStorage.getItem(ACCESS_TOKEN_KEY);
		const res = await fetch(
			`${API_BASE_URL}/api/v1/conversations/${activeId}/messages`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({ content: text }),
			},
		);
		setSending(false);

		if (!res.ok) {
			const msg = (await readApiErrorMessage(res)) || res.statusText;
			toast.error("Could not send: " + msg);
			return;
		}

		const newMsg = (await res.json()) as Message;
		setMessages((prev) => [...prev, newMsg]);
		setDraft("");
	}

	function otherUserId(c: Conversation) {
		if (!me) return c.user_two_id;
		return c.user_one_id === me.id ? c.user_two_id : c.user_one_id;
	}

	if (loading) {
		return (
			<main className="container mx-auto flex-1 px-4 py-8">
				<p className="text-sm text-muted-foreground">Loading...</p>
			</main>
		);
	}

	if (needsSignIn) {
		return (
			<main className="container mx-auto flex-1 px-4 py-8">
				<h1 className="text-2xl font-semibold">Messages</h1>
				<p className="mt-3 text-sm text-muted-foreground">
					You need to sign in to see your messages.
				</p>
				<Link
					href="/signin"
					className="mt-4 inline-block text-sm underline underline-offset-4"
				>
					Sign in
				</Link>
			</main>
		);
	}

	const active = conversations.find((c) => c.id === activeId) ?? null;

	return (
		<main className="container mx-auto flex-1 px-4 py-6">
			<h1 className="mb-4 text-2xl font-semibold">Messages</h1>

			{conversations.length === 0 ? (
				<p className="text-sm text-muted-foreground">
					No conversations yet. Open a listing and message the host to start one.
				</p>
			) : (
				<div className="grid gap-4 md:grid-cols-[260px_1fr]">
					<aside className="flex flex-col gap-1 rounded-lg border p-2">
						{conversations.map((c) => {
							const isActive = c.id === activeId;
							return (
								<button
									key={c.id}
									type="button"
									onClick={() => setActiveId(c.id)}
									className={
										"rounded-md px-3 py-2 text-left text-sm transition " +
										(isActive ? "bg-muted" : "hover:bg-muted/60")
									}
								>
									<div className="font-medium">User #{otherUserId(c)}</div>
									<div className="text-xs text-muted-foreground">
										listing #{c.listing_id}
									</div>
								</button>
							);
						})}
					</aside>

					<section className="flex h-[60vh] flex-col rounded-lg border">
						{active == null ? (
							<div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
								Pick a conversation
							</div>
						) : (
							<>
								<div className="flex-1 space-y-2 overflow-y-auto p-3">
									{messages.length === 0 && (
										<p className="text-center text-xs text-muted-foreground">
											No messages yet. Say hi.
										</p>
									)}
									{messages.map((m) => {
										const mine = me && m.sender_id === me.id;
										return (
											<div
												key={m.id}
												className={
													"flex " + (mine ? "justify-end" : "justify-start")
												}
											>
												<div
													className={
														"max-w-[75%] rounded-lg px-3 py-2 text-sm " +
														(mine
															? "bg-amber-500 text-amber-50"
															: "bg-muted")
													}
												>
													{m.content}
												</div>
											</div>
										);
									})}
									<div ref={bottomRef} />
								</div>

								<form
									className="flex gap-2 border-t p-2"
									onSubmit={(e) => {
										e.preventDefault();
										send();
									}}
								>
									<Input
										value={draft}
										onChange={(e) => setDraft(e.target.value)}
										placeholder="Write a message..."
										disabled={sending}
									/>
									<Button type="submit" disabled={sending || !draft.trim()}>
										Send
									</Button>
								</form>
							</>
						)}
					</section>
				</div>
			)}
		</main>
	);
}
