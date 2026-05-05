"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { ListingForm } from "@/components/listing-form";
import { ApiUnauthorizedError, fetchApiJson } from "@/lib/api";
import { clearTokens, getAccessToken } from "@/lib/auth";
import type { Listing } from "@/types/listing";

type MeResponse = { id: number; username: string };

export default function EditListingPage() {
	const router = useRouter();
	const params = useParams<{ id: string }>();
	const listingId = Number(params.id);

	const isInvalidId = !Number.isFinite(listingId) || listingId <= 0;

	const [listing, setListing] = useState<Listing | null>(null);
	const [loading, setLoading] = useState(!isInvalidId);
	const [error, setError] = useState<string | null>(
		isInvalidId ? "Invalid listing id." : null,
	);

	useEffect(() => {
		if (isInvalidId) return;
		const token = getAccessToken();
		if (!token) {
			router.replace("/signin");
			return;
		}

		let cancelled = false;
		(async () => {
			try {
				const me = await fetchApiJson<MeResponse>("/api/v1/users/me", token);
				const data = await fetchApiJson<Listing>(
					`/api/v1/listings/${listingId}`,
					token,
				);
				if (cancelled) return;
				if (data.host_id !== me.id) {
					setError("You can only edit your own listings.");
					return;
				}
				setListing(data);
			} catch (e) {
				if (e instanceof ApiUnauthorizedError) {
					clearTokens();
					toast.error(e.message);
					router.replace("/signin");
					return;
				}
				if (!cancelled) {
					setError(e instanceof Error ? e.message : String(e));
				}
			} finally {
				if (!cancelled) setLoading(false);
			}
		})();

		return () => {
			cancelled = true;
		};
	}, [listingId, router, isInvalidId]);

	if (loading) {
		return (
			<main className="container mx-auto flex max-w-5xl flex-1 items-center justify-center px-4 py-16">
				<p className="flex items-center gap-2 text-sm text-muted-foreground">
					<Loader2 className="size-4 animate-spin" aria-hidden />
					Loading listing…
				</p>
			</main>
		);
	}

	if (error || !listing) {
		return (
			<main className="container mx-auto max-w-5xl flex-1 px-4 py-16 text-center">
				<p className="text-sm text-destructive">{error ?? "Listing not found."}</p>
			</main>
		);
	}

	return (
		<main className="container mx-auto max-w-5xl px-4 py-10">
			<ListingForm mode="edit" listing={listing} listingId={listingId} />
		</main>
	);
}
