import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Listing } from "@/types/listing";

interface ListingCardProps {
	listing: Listing;
}

const dateFormat: Intl.DateTimeFormatOptions = {
	month: "short",
	day: "numeric",
	year: "numeric",
};

function formatRange(start: string, end: string) {
	const s = new Date(start).toLocaleDateString("en-US", dateFormat);
	const e = new Date(end).toLocaleDateString("en-US", dateFormat);
	return `${s} – ${e}`;
}

function formatPrice(price: number) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		maximumFractionDigits: 0,
	}).format(price);
}

export function ListingCard({ listing }: Readonly<ListingCardProps>) {
	const { title, location, price, start_date, end_date, thumbnail_url, room_type } = listing;

	return (
		<Card className="transition hover:ring-2 hover:ring-amber-500">
			{thumbnail_url ? (
				<Image
					src={thumbnail_url}
					alt={title}
					width={600}
					height={400}
					className="aspect-[3/2] w-full object-cover"
				/>
			) : (
				<div className="aspect-[3/2] w-full bg-muted" />
			)}

			<CardHeader>
				<CardTitle className="line-clamp-1">{title}</CardTitle>
				<CardDescription className="line-clamp-1">{location}</CardDescription>
			</CardHeader>

			<CardContent className="flex items-center justify-between">
				<span className="text-base font-semibold">
					{formatPrice(price)}
					<span className="text-sm font-normal text-muted-foreground"> / mo</span>
				</span>
				{room_type && (
					<span className="text-xs text-muted-foreground capitalize">{room_type}</span>
				)}
			</CardContent>

			<CardContent className="text-xs text-muted-foreground">
				{formatRange(start_date, end_date)}
			</CardContent>
		</Card>
	);
}
