"use client";

import { useEffect, useRef } from "react";
import { Map as MapLibre, type MapRef, Marker, NavigationControl } from "react-map-gl/maplibre";
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

	useEffect(() => {
		if (!flyTo) return;
		mapRef.current?.flyTo({
			center: [flyTo.longitude, flyTo.latitude],
			zoom: flyTo.zoom ?? 11,
			duration: 1500,
		});
	}, [flyTo]);

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
				<Marker key={pin.id} latitude={pin.latitude} longitude={pin.longitude} />
			))}
		</MapLibre>
	);
}
