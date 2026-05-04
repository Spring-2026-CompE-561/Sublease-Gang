import type { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { Calendar, MapPin, Star } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { BrowseListing } from "@/lib/listings";

const dateShortUtc: Intl.DateTimeFormatOptions = {
	timeZone: "UTC",
	month: "short",
	day: "numeric",
};

function formatRange(start: string, end: string) {
	const s = new Date(start).toLocaleDateString("en-US", dateShortUtc);
	const e = new Date(end).toLocaleDateString("en-US", dateShortUtc);
	return `${s} - ${e}`;
}

function formatPrice(price: number) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		maximumFractionDigits: 0,
	}).format(price);
}

interface ListingBrowseCardProps {
	readonly listing: BrowseListing;
	readonly className?: string;
	readonly actions?: ReactNode;
}

export function ListingBrowseCard({ listing, className, actions }: ListingBrowseCardProps) {
	const thumb = listing.thumbnail_url;
	const isDataUrl = Boolean(thumb?.startsWith("data:"));

	return (
		<Card
			className={cn(
				"overflow-hidden py-0 transition hover:ring-2 hover:ring-amber-500/80 focus-within:ring-2 focus-within:ring-ring",
				className,
			)}
		>
			<Link href={`/listings/${listing.id}`} className="group block outline-none">
				<div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
					{thumb && isDataUrl ? (
						// eslint-disable-next-line @next/next/no-img-element -- user-uploaded data URLs
						<img
							src={thumb}
							alt={listing.title}
							className="absolute inset-0 size-full object-cover transition duration-300 group-hover:scale-[1.02]"
						/>
					) : null}
					{thumb && !isDataUrl ? (
						<Image
							src={thumb}
							alt={listing.title}
							fill
							className="object-cover transition duration-300 group-hover:scale-[1.02]"
							sizes="(max-width: 640px) 100vw, (max-width: 1280px) 50vw, 33vw"
						/>
					) : null}
					{listing.verified ? (
						<span className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-full bg-background/95 px-2 py-0.5 text-xs font-medium text-foreground shadow-sm ring-1 ring-foreground/10 backdrop-blur-sm">
							Verified
						</span>
					) : null}
				</div>

				<div className="space-y-2 p-4">
					<div className="flex items-start justify-between gap-2">
						<h2 className="line-clamp-2 font-semibold leading-snug text-foreground">{listing.title}</h2>
						<span className="flex shrink-0 items-center gap-0.5 text-sm font-medium tabular-nums">
							<Star className="size-3.5 fill-foreground text-foreground" aria-hidden />
							{listing.rating.toFixed(1)}
						</span>
					</div>

					<p className="flex items-center gap-1.5 text-sm text-muted-foreground">
						<MapPin className="size-3.5 shrink-0" aria-hidden />
						<span className="line-clamp-1">{listing.location}</span>
					</p>

					<p className="flex items-center gap-1.5 text-sm text-muted-foreground">
						<Calendar className="size-3.5 shrink-0" aria-hidden />
						{formatRange(listing.start_date, listing.end_date)}
					</p>

					<p className="text-sm text-muted-foreground">{listing.university}</p>

					<p className="text-xs text-muted-foreground">
						<span className="font-medium text-foreground">{listing.bedrooms}</span> bed ·{" "}
						<span className="capitalize">{listing.room_type ?? "—"}</span> ·{" "}
						<span>{listing.sqft} sq ft</span>
					</p>

					{listing.amenities.length > 0 ? (
						<ul className="flex flex-wrap gap-1.5" aria-label="Amenities">
							{listing.amenities.slice(0, 5).map((a) => (
								<li
									key={a}
									className="rounded-full border border-border/80 bg-muted/50 px-2 py-0.5 text-xs text-muted-foreground"
								>
									{a}
								</li>
							))}
						</ul>
					) : null}

					<p className="pt-1 text-lg font-semibold">
						{formatPrice(listing.price)}
						<span className="text-sm font-normal text-muted-foreground"> / month</span>
					</p>
				</div>
			</Link>

			{actions ? <div className="flex gap-2 border-t px-4 py-3">{actions}</div> : null}
		</Card>
	);
}
