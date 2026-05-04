"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { API_BASE_URL, ACCESS_TOKEN_KEY, readApiErrorMessage } from "@/lib/api";

type Props = {
	listingId: number;
	hostId: number;
	className?: string;
};

export function MessageHostButton({ listingId, hostId, className }: Props) {
	const router = useRouter();
	const [busy, setBusy] = useState(false);

	async function handle() {
		const token = localStorage.getItem(ACCESS_TOKEN_KEY);
		if (!token) {
			toast.error("Sign in to message a host");
			router.push("/signin");
			return;
		}

		setBusy(true);
		const res = await fetch(`${API_BASE_URL}/api/v1/conversations/`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify({
				listing_id: listingId,
				other_user_id: hostId,
			}),
		});
		setBusy(false);

		if (!res.ok) {
			const msg = (await readApiErrorMessage(res)) || res.statusText;
			toast.error("Could not start conversation: " + msg);
			return;
		}

		router.push("/messages");
	}

	return (
		<Button type="button" onClick={handle} disabled={busy} className={className}>
			{busy ? "Starting..." : "Message host"}
		</Button>
	);
}
