import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export default function sitemap(): MetadataRoute.Sitemap {
	const now = new Date();
	const routes = ["/", "/listings", "/about", "/signin", "/signup"];

	return routes.map((path) => ({
		url: `${BASE_URL}${path}`,
		lastModified: now,
	}));
}
