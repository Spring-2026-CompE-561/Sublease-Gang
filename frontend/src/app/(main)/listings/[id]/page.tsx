import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ListingDetailView } from "@/components/listings/listing-detail-view";
import { getListingById } from "@/lib/listings";

type Props = {
	params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
	const { id } = await params;
	const listing = getListingById(id);
	if (!listing) return { title: "Listing not found | SubLease" };
	return {
		title: `${listing.title} | SubLease`,
		description: listing.description.slice(0, 160),
	};
}

export default async function ListingPage({ params }: Props) {
	const { id } = await params;
	const listing = getListingById(id);
	if (!listing) notFound();
	return <ListingDetailView listing={listing} />;
}
