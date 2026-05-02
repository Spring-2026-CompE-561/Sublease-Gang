import Hero from "@/components/home/Hero";
import Features from "@/components/home/features";
import CtaBanner from "@/components/home/cta-banner";
import { ListingCard } from "@/components/listings/listing-card";
import { mockListings } from "@/lib/listings";

export default function Home() {
	return (
		<main className="flex-1">
			<Hero />
			<Features />
			<section className="container mx-auto px-4 py-12">
				<h2 className="mb-6 text-2xl font-semibold">Available subleases</h2>
				<div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{mockListings.map((listing) => (
						<ListingCard key={listing.id} listing={listing} />
					))}
				</div>
			</section>
			<CtaBanner />
		</main>
	);
}
