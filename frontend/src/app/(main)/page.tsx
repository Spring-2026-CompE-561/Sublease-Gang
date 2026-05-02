import Hero from "@/components/home/Hero";
import Features from "@/components/home/features";
import CtaBanner from "@/components/home/cta-banner";
import { ListingBrowseCard } from "@/components/listings/listing-browse-card";
import { MOCK_BROWSE_LISTINGS } from "@/lib/listings";

const featuredListings = MOCK_BROWSE_LISTINGS.slice(0, 4);

export default function Home() {
	return (
		<main className="flex-1">
			<Hero />
			<Features />
			<section className="container mx-auto px-4 py-12">
				<h2 className="mb-6 text-2xl font-semibold">Available subleases</h2>
				<div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{featuredListings.map((listing) => (
						<ListingBrowseCard key={listing.id} listing={listing} />
					))}
				</div>
			</section>
			<CtaBanner />
		</main>
	);
}
