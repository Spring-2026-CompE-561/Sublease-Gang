"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
	Map as MapLibre,
	type MapRef,
	Marker,
	NavigationControl,
	Popup,
} from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const OSM_STYLE = {
	version: 8 as const,
	sources: {
		osm: {
			type: "raster" as const,
			tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
			tileSize: 256,
			attribution: "&copy; OpenStreetMap Contributors",
			maxzoom: 19,
		},
	},
	layers: [
		{
			id: "osm",
			type: "raster" as const,
			source: "osm",
		},
	],
};

export type MapPin = {
	id: string;
	latitude: number;
	longitude: number;
	title?: string;
	price?: number;
	thumbnailUrl?: string | null;
	location?: string;
};

export type FlyToTarget = {
	latitude: number;
	longitude: number;
	zoom?: number;
};

type MapProps = {
	pins?: MapPin[];
	initialLatitude?: number;
	initialLongitude?: number;
	initialZoom?: number;
	flyTo?: FlyToTarget;
};

export default function Map({
	pins = [],
	initialLatitude = 32.7157,
	initialLongitude = -117.1611,
	initialZoom = 12,
	flyTo,
}: MapProps) {
	const mapRef = useRef<MapRef>(null);
	const [activeId, setActiveId] = useState<string | null>(null);

	useEffect(() => {
		if (!flyTo) return;
		mapRef.current?.flyTo({
			center: [flyTo.longitude, flyTo.latitude],
			zoom: flyTo.zoom ?? 11,
			duration: 1500,
		});
	}, [flyTo]);

	useEffect(() => {
		if (activeId && !pins.some((p) => p.id === activeId)) {
			setActiveId(null);
		}
	}, [pins, activeId]);

	const active = activeId ? pins.find((p) => p.id === activeId) : null;

	return (
		<MapLibre
			ref={mapRef}
			initialViewState={{
				latitude: initialLatitude,
				longitude: initialLongitude,
				zoom: initialZoom,
			}}
			style={{ width: "100%", height: "100%" }}
			mapStyle={OSM_STYLE}
		>
			<NavigationControl position="top-right" />
			{pins.map((pin) => (
				<Marker
					key={pin.id}
					latitude={pin.latitude}
					longitude={pin.longitude}
					onClick={(e) => {
						e.originalEvent.stopPropagation();
						setActiveId((prev) => (prev === pin.id ? null : pin.id));
					}}
					style={{ cursor: "pointer" }}
				/>
			))}

			{active ? (
				<Popup
					latitude={active.latitude}
					longitude={active.longitude}
					anchor="bottom"
					offset={28}
					onClose={() => setActiveId(null)}
					closeOnClick={false}
					maxWidth="260px"
				>
					<Link
						href={`/listings/${active.id}?from=map`}
						className="block w-56 overflow-hidden rounded-lg bg-background text-foreground"
					>
						{active.thumbnailUrl ? (
							<div className="relative h-28 w-full">
								<Image
									src={active.thumbnailUrl}
									alt={active.title ?? "Listing"}
									fill
									sizes="224px"
									className="object-cover"
								/>
							</div>
						) : null}
						<div className="space-y-1 p-3">
							{active.title ? (
								<p className="line-clamp-2 text-sm font-medium leading-snug">{active.title}</p>
							) : null}
							{active.location ? (
								<p className="text-xs text-muted-foreground">{active.location}</p>
							) : null}
							{typeof active.price === "number" ? (
								<p className="text-sm font-semibold">${active.price}/mo</p>
							) : null}
							<p className="pt-1 text-xs font-medium text-primary underline-offset-2 hover:underline">
								View listing →
							</p>
						</div>
					</Link>
				</Popup>
			) : null}
		</MapLibre>
	);
}
