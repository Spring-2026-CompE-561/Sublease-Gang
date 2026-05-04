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

/** One row from `GET /api/v1/listings/` (differs from full `Listing`). */
export interface ListingListApiRow {
	id: number;
	title: string;
	price: number;
	college: number | null;
	location_text: string;
	room_type?: string | null;
	sqft?: number | null;
	start_date: string | null;
	end_date: string | null;
	thumbnail_url?: string | null;
	created_at: string | null;
}
