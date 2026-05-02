"use client";

import { Map as MapLibre, Marker, NavigationControl } from "react-map-gl/maplibre";
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

type MapProps = {
	pins?: MapPin[];
	initialLatitude?: number;
	initialLongitude?: number;
	initialZoom?: number;
};

export default function Map({
	pins = [],
	initialLatitude = 32.7157,
	initialLongitude = -117.1611,
	initialZoom = 12,
}: MapProps) {
	return (
		<MapLibre
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
