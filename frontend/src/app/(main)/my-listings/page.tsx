"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Pencil, Trash2 } from "lucide-react";
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
import { getAccessToken } from "@/lib/auth";
import { MOCK_MY_LISTINGS, type BrowseListing } from "@/lib/listings";

export default function MyListingsPage() {
	const router = useRouter();
	const [isAuthorized, setIsAuthorized] = useState(false);
	const [listings, setListings] = useState<BrowseListing[]>(MOCK_MY_LISTINGS);
	const [pendingDelete, setPendingDelete] = useState<BrowseListing | null>(null);

	useEffect(() => {
		const token = getAccessToken();
		if (!token) {
			router.push("/signin");
			return;
		}
		setIsAuthorized(true);
	}, [router]);

	function handleEdit(listing: BrowseListing) {
		toast.info(`Editing "${listing.title}" is coming soon.`);
	}

	function confirmDelete() {
		if (!pendingDelete) return;
		const removed = pendingDelete;
		setListings((prev) => prev.filter((l) => l.id !== removed.id));
		setPendingDelete(null);
		toast.success(`Removed "${removed.title}".`);
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
						{listings.length} listing{listings.length !== 1 ? "s" : ""}
					</p>
				</div>
			</div>

			<div className="mx-auto max-w-7xl px-4 py-8 md:px-6">
				{listings.length > 0 ? (
					<div className="grid auto-rows-max gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
						{listings.map((listing) => (
							<ListingBrowseCard
								key={listing.id}
								listing={listing}
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
							Posting subleases is coming soon.
						</p>
					</Card>
				)}
			</div>

			<Dialog
				open={pendingDelete !== null}
				onOpenChange={(open) => {
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
								<Button variant="outline" className="min-h-[44px] text-sm">
									Cancel
								</Button>
							}
						/>
						<Button
							variant="destructive"
							className="min-h-[44px] text-sm font-medium"
							onClick={confirmDelete}
						>
							Delete listing
						</Button>
					</DialogFooter>
				</DialogContent>
			</Dialog>
		</main>
	);
}
