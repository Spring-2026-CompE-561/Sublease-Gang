"use client";

import dynamic from "next/dynamic";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const SAMPLE_PINS = [
	{ id: "1", latitude: 32.8801, longitude: -117.234 },
	{ id: "2", latitude: 32.7503, longitude: -117.1859 },
	{ id: "3", latitude: 32.7157, longitude: -117.1611 },
];

export default function MapPage() {
	return (
		<main className="flex flex-1 flex-col">
			<div className="h-[calc(100vh-5rem)] w-full">
				<Map pins={SAMPLE_PINS} />
			</div>
		</main>
	);
}
