import { ImageResponse } from "next/og";

export const alt = "SubLease";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
	return new ImageResponse(
		(
			<div
				style={{
					height: "100%",
					width: "100%",
					display: "flex",
					flexDirection: "column",
					alignItems: "center",
					justifyContent: "center",
					background: "linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%)",
					color: "#1f2937",
					fontFamily: "sans-serif",
				}}
			>
				<div style={{ fontSize: 96, fontWeight: 700 }}>SubLease</div>
				<div style={{ fontSize: 32, marginTop: 16, color: "#4b5563" }}>
					Find your next sublease near campus
				</div>
			</div>
		),
		size,
	);
}
