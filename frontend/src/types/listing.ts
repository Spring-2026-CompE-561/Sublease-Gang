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
