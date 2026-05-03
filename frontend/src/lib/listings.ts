import type { Listing } from "@/types/listing";

/** Listing fields used on browse + cards (mock/API may grow over time). */
export type BrowseListing = Listing & {
	rating: number;
	university: string;
	verified: boolean;
	bedrooms: number;
	amenities: string[];
};

export const PRICE_FILTER_MAX = 2000;
export const SQFT_FILTER_MAX = 2000;

export const AMENITY_OPTIONS = [
	"WiFi",
	"Furnished",
	"Utilities Included",
	"Parking",
	"Laundry",
	"Kitchen",
	"Air Conditioning",
	"Pool",
	"Gym Access",
] as const;

export type AmenityId = (typeof AMENITY_OPTIONS)[number];

/** Mock catalog aligned with Figma “All Listings”. */
export const MOCK_BROWSE_LISTINGS: BrowseListing[] = [
	{
		id: 1,
		host_id: 1,
		title: "Modern Studio Near Campus",
		description: "Compact studio blocks from campus.",
		price: 850,
		location: "Downtown Berkeley",
		room_type: "studio",
		sqft: 380,
		start_date: "2026-05-14T00:00:00Z",
		end_date: "2026-08-30T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
		latitude: 37.8715,
		longitude: -122.273,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.9,
		university: "UC Berkeley",
		verified: true,
		bedrooms: 1,
		amenities: ["WiFi", "Furnished", "Kitchen", "Laundry"],
	},
	{
		id: 2,
		host_id: 2,
		title: "Cozy Dorm Room Available",
		description: "Quiet dorm-style setup for summer.",
		price: 650,
		location: "West Campus",
		room_type: "private room",
		sqft: 180,
		start_date: "2026-05-31T00:00:00Z",
		end_date: "2026-08-14T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1595526114035-0d68ed016cf2?auto=format&fit=crop&w=800&q=80",
		latitude: 37.4275,
		longitude: -122.1697,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.7,
		university: "Stanford University",
		verified: true,
		bedrooms: 1,
		amenities: ["WiFi", "Furnished", "Laundry", "Gym Access"],
	},
	{
		id: 3,
		host_id: 3,
		title: "Spacious 1BR in Student Housing",
		description: "One bedroom in purpose-built student housing.",
		price: 1100,
		location: "University District",
		room_type: "1 bedroom",
		sqft: 620,
		start_date: "2026-05-19T00:00:00Z",
		end_date: "2026-09-09T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
		latitude: 34.0689,
		longitude: -118.4452,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 5,
		university: "UCLA",
		verified: true,
		bedrooms: 1,
		amenities: ["WiFi", "Utilities Included", "Gym Access", "Air Conditioning"],
	},
	{
		id: 4,
		host_id: 4,
		title: "Shared Apartment - Private Room",
		description: "Private bedroom in a friendly shared flat.",
		price: 700,
		location: "North Campus",
		room_type: "private room",
		sqft: 140,
		start_date: "2026-06-09T00:00:00Z",
		end_date: "2026-08-19T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
		latitude: 42.3601,
		longitude: -71.0942,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.5,
		university: "MIT",
		verified: true,
		bedrooms: 1,
		amenities: ["WiFi", "Kitchen", "Laundry"],
	},
	{
		id: 5,
		host_id: 5,
		title: "Modern Apartment with Kitchen",
		description: "Updated kitchen and fast commute to classes.",
		price: 950,
		location: "East Side",
		room_type: "2 bedroom",
		sqft: 780,
		start_date: "2026-05-24T00:00:00Z",
		end_date: "2026-08-24T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=800&q=80",
		latitude: 40.8075,
		longitude: -73.9626,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.8,
		university: "Columbia University",
		verified: true,
		bedrooms: 2,
		amenities: ["WiFi", "Kitchen", "Utilities Included", "Air Conditioning"],
	},
	{
		id: 6,
		host_id: 6,
		title: "Bright Living Space Near University",
		description: "Sunny layout close to transit and dining.",
		price: 800,
		location: "South Campus",
		room_type: "1 bedroom",
		sqft: 540,
		start_date: "2026-06-04T00:00:00Z",
		end_date: "2026-08-29T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80",
		latitude: 40.7295,
		longitude: -73.9965,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.6,
		university: "NYU",
		verified: true,
		bedrooms: 1,
		amenities: ["WiFi", "Furnished", "Kitchen", "Utilities Included"],
	},
	{
		id: 7,
		host_id: 7,
		title: "Sunny 2BR Steps from SDSU",
		description: "Light-filled apartment minutes from College Ave trolley stop.",
		price: 1250,
		location: "College Area",
		room_type: "2 bedroom",
		sqft: 720,
		start_date: "2026-05-20T00:00:00Z",
		end_date: "2026-08-25T00:00:00Z",
		college_id: null,
		thumbnail_url:
			"https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80",
		latitude: 32.7757,
		longitude: -117.0719,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.7,
		university: "San Diego State University",
		verified: true,
		bedrooms: 2,
		amenities: ["WiFi", "Furnished", "Parking", "Air Conditioning", "Laundry"],
	},
];

/** Mock saved listings - subset of browse listings for user's saved collection. */
export const MOCK_SAVED_LISTINGS: BrowseListing[] = [
	MOCK_BROWSE_LISTINGS[0], // Modern Studio Near Campus
	MOCK_BROWSE_LISTINGS[2], // Spacious 1BR in Student Housing
	MOCK_BROWSE_LISTINGS[4], // Modern Apartment with Kitchen
];

/** Mock reported listings - subset of browse listings that user has reported. */
export const MOCK_REPORTED_LISTINGS: BrowseListing[] = [
	MOCK_BROWSE_LISTINGS[1], // Cozy Dorm Room Available
	MOCK_BROWSE_LISTINGS[3], // Shared Apartment - Private Room
];

export interface BrowseFiltersState {
	priceMin: number;
	priceMax: number;
	sqftMin: number;
	sqftMax: number;
	bedrooms: number | null;
	amenities: Set<string>;
	university: string | null;
}

export const UNIVERSITY_OPTIONS = Array.from(
	new Set(MOCK_BROWSE_LISTINGS.map((l) => l.university)),
).sort();

export function filterBrowseListings(
	listings: BrowseListing[],
	f: BrowseFiltersState,
): BrowseListing[] {
	return listings.filter((l) => {
		if (l.price < f.priceMin || l.price > f.priceMax) return false;
		if (l.sqft < f.sqftMin || l.sqft > f.sqftMax) return false;
		if (f.bedrooms != null && l.bedrooms !== f.bedrooms) return false;
		if (f.university && l.university !== f.university) return false;
		for (const a of f.amenities) {
			if (!l.amenities.includes(a)) return false;
		}
		return true;
	});
}

export function getBrowseListingById(id: string): BrowseListing | undefined {
	const n = Number(id);
	if (!Number.isFinite(n)) return undefined;
	return MOCK_BROWSE_LISTINGS.find((l) => l.id === n);
}
