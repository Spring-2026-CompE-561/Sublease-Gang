import { Navbar } from "@/components/Navbar";
import Footer from "@/components/Footer";
import { ListingCard } from "@/components/ListingCard";
import type { Listing } from "@/types/listing";

const mockListings: Listing[] = [
	{
		id: 1,
		host_id: 1,
		title: "Cozy studio near campus",
		description: "Quiet studio, walkable to lecture halls.",
		price: 1200,
		location: "San Diego, CA",
		room_type: "studio",
		sqft: 420,
		start_date: "2026-06-01T00:00:00Z",
		end_date: "2026-08-31T00:00:00Z",
		college_id: null,
		thumbnail_url: null,
		latitude: 32.7157,
		longitude: -117.1611,
		created_at: "2026-04-01T00:00:00Z",
		updated_at: "2026-04-01T00:00:00Z",
	},
	{
		id: 2,
		host_id: 2,
		title: "Sunny 1BR with balcony",
		description: "Top floor unit with great light and a small balcony.",
		price: 1850,
		location: "Berkeley, CA",
		room_type: "1 bedroom",
		sqft: 650,
		start_date: "2026-05-15T00:00:00Z",
		end_date: "2026-08-15T00:00:00Z",
		college_id: null,
		thumbnail_url: null,
		latitude: 37.8715,
		longitude: -122.273,
		created_at: "2026-04-02T00:00:00Z",
		updated_at: "2026-04-02T00:00:00Z",
	},
	{
		id: 3,
		host_id: 3,
		title: "Shared 2BR, private room",
		description: "Private bedroom in shared apartment, friendly roommates.",
		price: 950,
		location: "Los Angeles, CA",
		room_type: "private room",
		sqft: 220,
		start_date: "2026-06-10T00:00:00Z",
		end_date: "2026-09-10T00:00:00Z",
		college_id: null,
		thumbnail_url: null,
		latitude: 34.0522,
		longitude: -118.2437,
		created_at: "2026-04-03T00:00:00Z",
		updated_at: "2026-04-03T00:00:00Z",
	},
	{
		id: 4,
		host_id: 4,
		title: "Modern loft downtown",
		description: "Bright loft, walking distance to coffee and transit.",
		price: 2100,
		location: "Seattle, WA",
		room_type: "loft",
		sqft: 720,
		start_date: "2026-07-01T00:00:00Z",
		end_date: "2026-09-30T00:00:00Z",
		college_id: null,
		thumbnail_url: null,
		latitude: 47.6062,
		longitude: -122.3321,
		created_at: "2026-04-04T00:00:00Z",
		updated_at: "2026-04-04T00:00:00Z",
	},
];

export default function Home() {
	return (
		<div className="flex min-h-screen flex-col">
			<Navbar />
			<main className="container mx-auto flex-1 px-4 py-8">
				<h1 className="mb-6 text-2xl font-semibold">Available subleases</h1>
				<div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
					{mockListings.map((listing) => (
						<ListingCard key={listing.id} listing={listing} />
					))}
				</div>
			</main>
			<Footer />
		</div>
	);
}
