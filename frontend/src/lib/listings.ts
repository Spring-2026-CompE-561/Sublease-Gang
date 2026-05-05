import type { Listing, ListingListApiRow } from "@/types/listing";
import {
	ACCESS_TOKEN_KEY,
	API_BASE_URL,
	deleteApiJson,
	fetchApiJson,
	postApiJson,
} from "@/lib/api";

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
		college_id: 1,
		thumbnail_url:
			"https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
		latitude: 37.8715,
		longitude: -122.273,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		rating: 4.9,
		university: "UC Berkeley",
		verified: true,
		bedrooms: 0,
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
		college_id: 2,
		thumbnail_url:
			"https://images.unsplash.com/photo-1631679706909-1844bbd07221?auto=format&fit=crop&w=800&q=80",
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
		college_id: 3,
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
		college_id: 4,
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
		college_id: 5,
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
		college_id: 6,
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
		college_id: 7,
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

/** Mock listings owned by the signed-in user. */
export const MOCK_MY_LISTINGS: BrowseListing[] = [
	MOCK_BROWSE_LISTINGS[1], // Cozy Dorm Room Available
	MOCK_BROWSE_LISTINGS[5], // Bright Living Space Near University
];

export interface BrowseFiltersState {
	priceMin: number;
	priceMax: number;
	sqftMin: number;
	sqftMax: number;
	bedrooms: number | null;
	amenities: Set<string>;
	collegeId: number | null;
}

export type CollegeFilterOption = { id: number; label: string };

/** College labels from mock browse data (map page and fallback when API filters fail). */
export function collegeOptionsFromMockListings(): CollegeFilterOption[] {
	const byId = new Map<number, string>();
	for (const l of MOCK_BROWSE_LISTINGS) {
		if (l.college_id != null && l.university) {
			byId.set(l.college_id, l.university);
		}
	}
	return Array.from(byId.entries())
		.map(([id, label]) => ({ id, label }))
		.sort((a, b) => a.label.localeCompare(b.label));
}

export async function fetchCollegeFilterOptions(): Promise<CollegeFilterOption[]> {
	const merged = new Map<number, string>();
	for (const opt of collegeOptionsFromMockListings()) {
		merged.set(opt.id, opt.label);
	}
	try {
		const res = await fetch(`${API_BASE_URL}/api/v1/listings/filters`);
		if (!res.ok) {
			return collegeOptionsFromMockListings();
		}
		const data = (await res.json()) as {
			colleges?: { id: number; name: string | number }[];
		};
		for (const c of data.colleges ?? []) {
			const nameStr =
				typeof c.name === "string" ? c.name.trim() : String(c.name);
			const looksLikeRealName = nameStr.length > 0 && Number(nameStr) !== c.id;
			const label = looksLikeRealName ? nameStr : (merged.get(c.id) ?? `College ${c.id}`);
			merged.set(c.id, label);
		}
	} catch {
		return collegeOptionsFromMockListings();
	}
	return Array.from(merged.entries())
		.map(([id, label]) => ({ id, label }))
		.sort((a, b) => a.label.localeCompare(b.label));
}

export function filterBrowseListings(
	listings: BrowseListing[],
	f: BrowseFiltersState,
): BrowseListing[] {
	return listings.filter((l) => {
		if (l.price < f.priceMin || l.price > f.priceMax) return false;
		const sqft = l.sqft ?? 0;
		if (sqft < f.sqftMin || sqft > f.sqftMax) return false;
		if (f.bedrooms != null && l.bedrooms !== f.bedrooms) return false;
		if (f.collegeId != null && (l.college_id ?? null) !== f.collegeId) return false;
		for (const a of f.amenities) {
			if (!l.amenities.includes(a)) return false;
		}
		return true;
	});
}

/** Map browse list API row into full `Listing` (defaults for omitted fields). */
export function listingFromListRow(row: ListingListApiRow): Listing {
	return {
		id: row.id,
		host_id: 0,
		title: row.title,
		description: "",
		price: row.price,
		location: row.location_text ?? "",
		room_type: row.room_type ?? null,
		sqft: row.sqft ?? null,
		start_date: row.start_date ?? "",
		end_date: row.end_date ?? "",
		college_id: row.college ?? null,
		thumbnail_url: row.thumbnail_url ?? null,
		latitude: row.latitude ?? 0,
		longitude: row.longitude ?? 0,
		created_at: row.created_at ?? "",
		updated_at: row.created_at ?? "",
	};
}

// API doesn't return rating/university/verified/bedrooms/amenities yet,
// so fill them with sensible defaults.
function bedroomsFromRoomType(roomType: string | null | undefined): number {
	if (!roomType) return 1;
	const lower = roomType.toLowerCase();
	if (lower.includes("studio")) return 0;
	const m = lower.match(/(\d+)/);
	return m ? Number(m[1]) : 1;
}

export function toBrowseListing(l: Listing): BrowseListing {
	return {
		...l,
		rating: 0,
		university: "",
		verified: false,
		bedrooms: bedroomsFromRoomType(l.room_type),
		amenities: [],
	};
}

type FetchBrowseOptions = {
	limit?: number;
};

export async function fetchBrowseListings(
	options: FetchBrowseOptions = {},
): Promise<BrowseListing[]> {
	const limit = options.limit ?? 100;
	const init: RequestInit =
		typeof window === "undefined" ? { next: { revalidate: 30 } } : {};
	const res = await fetch(`${API_BASE_URL}/api/v1/listings/?limit=${limit}`, init);
	if (!res.ok) {
		throw new Error("Failed to load listings");
	}
	const data = (await res.json()) as { results: ListingListApiRow[] };
	return data.results.map((row) => toBrowseListing(listingFromListRow(row)));
}

export async function fetchListingsByHost(hostId: number): Promise<BrowseListing[]> {
	const qs = new URLSearchParams({ host_id: String(hostId), limit: "100" });
	const res = await fetch(`${API_BASE_URL}/api/v1/listings/?${qs.toString()}`);
	if (!res.ok) {
		throw new Error("Failed to load listings");
	}
	const data = (await res.json()) as { results: ListingListApiRow[] };
	return data.results.map((row) => toBrowseListing(listingFromListRow(row)));
}

function browseListingFromMockId(id: number): BrowseListing | undefined {
	return MOCK_BROWSE_LISTINGS.find((l) => l.id === id);
}

function readAccessToken(): string | null {
	if (typeof window === "undefined") return null;
	return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export async function fetchSavedListings(): Promise<BrowseListing[]> {
	const token = readAccessToken();
	if (!token) throw new Error("Not signed in");
	const rows = await fetchApiJson<Listing[]>("/api/v1/saved-listings/", token);
	return rows.map(toBrowseListing);
}

export async function saveListing(listingId: number): Promise<void> {
	const token = readAccessToken();
	if (!token) throw new Error("Not signed in");
	await postApiJson<Listing, Record<string, never>>(
		`/api/v1/saved-listings/${listingId}`,
		token,
		{},
	);
}

export async function unsaveListing(listingId: number): Promise<void> {
	const token = readAccessToken();
	if (!token) throw new Error("Not signed in");
	await deleteApiJson(`/api/v1/saved-listings/${listingId}`, token);
}

/** Server or client: load one listing from the API, falling back to mock data for demos. */
export async function fetchBrowseListingById(id: string): Promise<BrowseListing | null> {
	const n = Number(id);
	if (!Number.isFinite(n)) return null;

	const fromMock = browseListingFromMockId(n);

	try {
		const init: RequestInit =
			typeof window === "undefined" ? { next: { revalidate: 30 } } : {};
		const res = await fetch(`${API_BASE_URL}/api/v1/listings/${n}`, init);
		if (res.ok) {
			const data = (await res.json()) as Listing;
			return toBrowseListing(data);
		}
	} catch {
		// offline / SSR build without API
	}

	return fromMock ?? null;
}
