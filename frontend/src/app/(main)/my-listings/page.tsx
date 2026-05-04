"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2, Pencil, Trash2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { ListingBrowseCard } from "@/components/listings/listing-browse-card";
import { ApiUnauthorizedError, deleteApiJson, fetchApiJson } from "@/lib/api";
import { clearTokens, getAccessToken } from "@/lib/auth";
import { fetchListingsByHost, type BrowseListing } from "@/lib/listings";

type MeResponse = { id: number; username: string };

export default function MyListingsPage() {
	const router = useRouter();
	const [isAuthorized, setIsAuthorized] = useState(false);
	const [listings, setListings] = useState<BrowseListing[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [pendingDelete, setPendingDelete] = useState<BrowseListing | null>(null);
	const [deleteBusy, setDeleteBusy] = useState(false);

	const loadMyListings = useCallback(async () => {
		const token = getAccessToken();
		if (!token) {
			router.push("/signin");
			return;
		}

		setLoading(true);
		setError(null);

		try {
			const me = await fetchApiJson<MeResponse>("/api/v1/users/me", token);
			const rows = await fetchListingsByHost(me.id);
			setListings(rows);
			setIsAuthorized(true);
		} catch (e) {
			if (e instanceof ApiUnauthorizedError) {
				clearTokens();
				toast.error(e.message);
				router.replace("/signin");
				return;
			}
			const message = e instanceof Error ? e.message : String(e);
			setError(message);
			setIsAuthorized(true);
		} finally {
			setLoading(false);
		}
	}, [router]);

	useEffect(() => {
		void loadMyListings();
	}, [loadMyListings]);

	function handleEdit(listing: BrowseListing) {
		toast.info(`Editing "${listing.title}" is coming soon.`);
	}

	async function confirmDelete() {
		if (!pendingDelete) return;
		const token = getAccessToken();
		if (!token) {
			router.replace("/signin");
			return;
		}

		const removed = pendingDelete;
		setDeleteBusy(true);
		try {
			await deleteApiJson(`/api/v1/listings/${removed.id}`, token);
			setListings((prev) => prev.filter((l) => l.id !== removed.id));
			setPendingDelete(null);
			toast.success(`Removed "${removed.title}".`);
		} catch (e) {
			if (e instanceof ApiUnauthorizedError) {
				clearTokens();
				toast.error(e.message);
				router.replace("/signin");
				return;
			}
			const message = e instanceof Error ? e.message : String(e);
			toast.error(message);
		} finally {
			setDeleteBusy(false);
		}
	}

	if (!isAuthorized && loading) {
		return (
			<main className="flex flex-1 items-center justify-center px-4 py-16">
				<p className="flex items-center gap-2 text-sm text-muted-foreground">
					<Loader2 className="size-4 animate-spin" aria-hidden />
					Loading your listings…
				</p>
			</main>
		);
	}

	if (!isAuthorized) {
		return (
			<main className="flex-1 px-4 py-16 text-center">
				<p className="text-muted-foreground">Redirecting to sign in...</p>
			</main>
		);
	}

	return (
		<main className="flex-1">
			<div className="border-b bg-background">
				<div className="mx-auto max-w-7xl px-4 py-6 md:px-6">
					<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">My Listings</h1>
					<p className="mt-1 text-sm text-muted-foreground">
						{loading
							? "Loading…"
							: `${listings.length} listing${listings.length !== 1 ? "s" : ""}`}
					</p>
				</div>
			</div>

			<div className="mx-auto max-w-7xl px-4 py-8 md:px-6">
				{loading ? (
					<Card className="flex flex-col items-center justify-center gap-3 py-16">
						<Loader2 className="size-6 animate-spin text-muted-foreground" aria-hidden />
						<p className="text-sm text-muted-foreground">Loading your listings…</p>
					</Card>
				) : error ? (
					<Card className="flex flex-col items-center justify-center gap-3 py-16">
						<p className="text-sm text-destructive">{error}</p>
						<Button variant="outline" size="sm" onClick={() => void loadMyListings()}>
							Try again
						</Button>
					</Card>
				) : listings.length > 0 ? (
					<div className="grid auto-rows-max gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
						{listings.map((listing) => (
							<ListingBrowseCard
								key={listing.id}
								listing={listing}
								from="my-listings"
								actions={
									<>
										<Button
											variant="outline"
											size="sm"
											className="flex-1"
											onClick={() => handleEdit(listing)}
										>
											<Pencil className="size-3.5" aria-hidden />
											Edit
										</Button>
										<Button
											variant="destructive"
											size="sm"
											className="flex-1"
											onClick={() => setPendingDelete(listing)}
										>
											<Trash2 className="size-3.5" aria-hidden />
											Delete
										</Button>
									</>
								}
							/>
						))}
					</div>
				) : (
					<Card className="flex flex-col items-center justify-center gap-3 py-16">
						<p className="text-lg font-medium text-foreground">No listings yet</p>
						<p className="text-sm text-muted-foreground">
							You haven&apos;t posted any subleases yet.
						</p>
					</Card>
				)}
			</div>

			<Dialog
				open={pendingDelete !== null}
				onOpenChange={(open) => {
					if (deleteBusy) return;
					if (!open) setPendingDelete(null);
				}}
			>
				<DialogContent>
					<DialogHeader>
						<DialogTitle>Delete this listing?</DialogTitle>
						<DialogDescription>
							{pendingDelete
								? `"${pendingDelete.title}" will be removed from your active listings. This action cannot be undone.`
								: null}
						</DialogDescription>
					</DialogHeader>
					<DialogFooter>
						<DialogClose
							render={
								<Button
									variant="outline"
									className="min-h-[44px] text-sm"
									disabled={deleteBusy}
								>
									Cancel
								</Button>
							}
						/>
						<Button
							variant="destructive"
							className="min-h-[44px] text-sm font-medium"
							disabled={deleteBusy}
							onClick={() => void confirmDelete()}
						>
							{deleteBusy ? (
								<>
									<Loader2 className="mr-2 size-4 animate-spin" aria-hidden />
									Deleting…
								</>
							) : (
								"Delete listing"
							)}
						</Button>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</main>
	);
}
