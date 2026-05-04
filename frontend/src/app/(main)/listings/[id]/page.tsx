import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ArrowLeft, Calendar, MapPin, Star } from "lucide-react";
import { Card } from "@/components/ui/card";
import { MessageHostButton } from "@/components/MessageHostButton";
import { ReportListingDialog } from "@/components/report-listing-dialog";
import { fetchBrowseListingById } from "@/lib/listings";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
	const { id } = await params;
	const listing = await fetchBrowseListingById(id);
	if (!listing) return { title: "Listing | SubLease" };
	return {
		title: `${listing.title} | SubLease`,
		description: listing.description.slice(0, 160),
	};
}

function formatRange(start: string, end: string) {
	const s = new Date(start).toLocaleDateString("en-US", {
		timeZone: "UTC",
		month: "short",
		day: "numeric",
		year: "numeric",
	});
	const e = new Date(end).toLocaleDateString("en-US", {
		timeZone: "UTC",
		month: "short",
		day: "numeric",
		year: "numeric",
	});
	return `${s} – ${e}`;
}

function formatPrice(price: number) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		maximumFractionDigits: 0,
	}).format(price);
}

export default async function ListingDetailPage({ params }: Props) {
	const { id } = await params;
	const listing = await fetchBrowseListingById(id);
	if (!listing) notFound();

	const hero = listing.thumbnail_url;

	return (
		<main className="flex-1">
			<div className="border-b bg-background">
				<div className="mx-auto max-w-6xl px-4 py-3 md:px-6">
					<Link
						href="/listings"
						className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition hover:text-foreground"
					>
						<ArrowLeft className="size-4" aria-hidden />
						Back to all listings
					</Link>
				</div>
			</div>

			<div className="mx-auto max-w-6xl px-4 py-8 md:px-6">
				{hero ? (
					<div className="relative mb-8 overflow-hidden rounded-2xl ring-1 ring-foreground/10">
						<Image
							src={hero}
							alt={listing.title}
							width={1600}
							height={900}
							className="aspect-video w-full object-cover"
							priority
							sizes="(max-width: 768px) 100vw, min(1152px, 100vw)"
						/>
					</div>
				) : (
					<div className="mb-8 aspect-video rounded-2xl bg-muted" />
				)}

				<div className="mb-6 flex flex-wrap items-start justify-between gap-4">
					<div>
						<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{listing.title}</h1>
						<div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
							<span className="inline-flex items-center gap-1">
								<MapPin className="size-4 shrink-0" aria-hidden />
								{listing.location}
							</span>
							{listing.rating > 0 ? (
								<>
									<span className="text-border">·</span>
									<span className="inline-flex items-center gap-1 font-medium text-foreground">
										<Star className="size-4 fill-foreground text-foreground" aria-hidden />
										{listing.rating.toFixed(1)}
									</span>
								</>
							) : null}
						</div>
						{listing.university.trim().length > 0 ? (
							<p className="mt-2 text-sm text-muted-foreground">{listing.university}</p>
						) : null}
					</div>
					{listing.verified ? (
						<span className="rounded-full bg-muted px-3 py-1 text-xs font-medium">Verified</span>
					) : null}
				</div>

				<div className="grid gap-8 lg:grid-cols-[1fr_320px] lg:items-start">
					<div className="space-y-4">
						<section>
							<h2 className="mb-2 text-lg font-semibold">About</h2>
							<p className="text-muted-foreground leading-relaxed">{listing.description}</p>
						</section>
						<section className="flex items-center gap-2 text-sm text-muted-foreground">
							<Calendar className="size-4 shrink-0" aria-hidden />
							{formatRange(listing.start_date, listing.end_date)}
						</section>
						{listing.amenities.length > 0 ? (
							<section>
								<h2 className="mb-2 text-lg font-semibold">Amenities</h2>
								<ul className="flex flex-wrap gap-2">
									{listing.amenities.map((a) => (
										<li
											key={a}
											className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-foreground"
										>
											{a}
										</li>
									))}
								</ul>
							</section>
						) : null}
					</div>

					<Card className="gap-0 p-6 shadow-md ring-foreground/15 lg:sticky lg:top-24">
						<p className="text-2xl font-semibold">
							{formatPrice(listing.price)}
							<span className="text-base font-normal text-muted-foreground"> / month</span>
						</p>
						<p className="mt-1 text-sm text-muted-foreground capitalize">{listing.room_type}</p>
						<MessageHostButton
							listingId={listing.id}
							hostId={listing.host_id}
							className="mt-6 w-full justify-center rounded-xl"
						/>
						<p className="mt-3 text-center text-xs text-muted-foreground">You won&apos;t be charged yet.</p>
						<ReportListingDialog listingId={String(listing.id)} />
					</Card>
				</div>
			</div>
		</main>
	);
}
