import Link from "next/link";

export default function MapPage() {
	return (
		<main className="container mx-auto flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
			<h1 className="text-3xl font-semibold">Map</h1>
			<p className="mt-3 max-w-md text-sm text-muted-foreground">
				The interactive map view is coming soon. You&apos;ll be able to browse subleases by location.
			</p>
			<Link href="/listings" className="mt-6 text-sm underline underline-offset-4">
				Back to listings
			</Link>
		</main>
	);
}
