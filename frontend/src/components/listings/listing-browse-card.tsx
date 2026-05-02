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
}

export function ListingBrowseCard({ listing, className }: ListingBrowseCardProps) {
	const thumb = listing.thumbnail_url;

	return (
		<Link href={`/listings/${listing.id}`} className={cn("group block outline-none", className)}>
			<Card className="overflow-hidden py-0 transition hover:ring-2 hover:ring-amber-500/80 focus-visible:ring-2 focus-visible:ring-ring">
				<div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
					{thumb ? (
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

					<p className="pt-1 text-lg font-semibold">
						{formatPrice(listing.price)}
						<span className="text-sm font-normal text-muted-foreground"> / month</span>
					</p>
				</div>
			</Card>
		</Link>
	);
}
