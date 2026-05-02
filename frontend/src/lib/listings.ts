/**
 * Listing domain types, mock data, and helpers (mirrors `src/lib/dashboard.ts` style in proffessor-frontend).
 */

export interface Listing {
	id: number;
	host_id: number;
	title: string;
	description: string;
	price: number;
	location: string;
	room_type?: string | null;
	sqft?: number | null;
	start_date: string;
	end_date: string;
	college_id?: number | null;
	thumbnail_url?: string | null;
	latitude: number;
	longitude: number;
	created_at: string;
	updated_at: string;
}

/** Optional fields for listing detail (mock/API may populate over time). */
export type ListingWithDetail = Listing & {
	university?: string | null;
	rating?: number;
	review_count?: number;
	host_name?: string;
	host_initials?: string;
	host_verified?: boolean;
	host_subtitle?: string;
	amenities?: string[];
	bathrooms?: number;
	bedrooms?: number;
	hero_image_url?: string | null;
	wifi_included?: boolean;
};

export const mockListings: ListingWithDetail[] = [
	{
		id: 1,
		host_id: 1,
		title: "Cozy Dorm Room Available",
		description:
			"This quiet dorm setup is perfect for summer session or an internship quarter. Desk, Wi‑Fi, and shared laundry are all nearby. Roommates are respectful and keep common spaces tidy.",
		price: 650,
		location: "West Campus",
		room_type: "private room",
		sqft: 180,
		start_date: "2026-05-31T00:00:00Z",
		end_date: "2026-08-14T00:00:00Z",
		college_id: null,
		thumbnail_url: "/images/listing-hero-sample.png",
		hero_image_url: "/images/listing-hero-sample.png",
		latitude: 37.4275,
		longitude: -122.1697,
		created_at: "2026-04-01T00:00:00Z",
		updated_at: "2026-04-01T00:00:00Z",
		university: "Stanford University",
		rating: 4.7,
		review_count: 8,
		host_name: "Michael Torres",
		host_initials: "MT",
		host_verified: true,
		host_subtitle: "University verified student.",
		amenities: ["WiFi", "Study Lounge", "Furnished", "Gym Access"],
		bathrooms: 1,
		bedrooms: 1,
		wifi_included: true,
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
		rating: 4.9,
		review_count: 12,
		host_name: "Alex Chen",
		host_initials: "AC",
		host_verified: true,
		host_subtitle: "Hosts often respond within an hour.",
		amenities: ["WiFi", "In-unit laundry", "Furnished", "Balcony"],
		bathrooms: 1,
		bedrooms: 1,
		wifi_included: true,
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
		host_name: "Jordan Lee",
		host_initials: "JL",
		amenities: ["WiFi", "Kitchen", "Furnished"],
		bathrooms: 1,
		bedrooms: 1,
		wifi_included: true,
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
		host_name: "Sam Rivera",
		host_initials: "SR",
		amenities: ["WiFi", "Gym", "Furnished", "Doorman"],
		bathrooms: 1,
		bedrooms: 1,
		wifi_included: true,
	},
];

export function getListingById(id: string): ListingWithDetail | undefined {
	const n = Number(id);
	if (!Number.isFinite(n)) return undefined;
	return mockListings.find((l) => l.id === n);
}

const dateLongUtc: Intl.DateTimeFormatOptions = {
	timeZone: "UTC",
	month: "long",
	day: "numeric",
	year: "numeric",
};

export function formatListingLongDate(iso: string) {
	return new Date(iso).toLocaleDateString("en-US", dateLongUtc);
}

export function formatListingCurrency(n: number) {
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		maximumFractionDigits: 0,
	}).format(n);
}

/** Rough month count for price estimates (mock parity with earlier UI). */
export function estimatedLeaseMonths(startIso: string, endIso: string): number {
	const start = new Date(startIso).getTime();
	const end = new Date(endIso).getTime();
	const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
	return Math.max(1, Math.ceil(days / 30));
}

export function listingHeroSrc(listing: ListingWithDetail): string | null {
	return listing.hero_image_url ?? listing.thumbnail_url ?? null;
}
