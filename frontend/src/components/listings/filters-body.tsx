"use client";

import { AMENITY_OPTIONS, ROOM_TYPE_OPTIONS, UNIVERSITY_OPTIONS } from "@/lib/listings";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";

const ANY_UNIVERSITY = "__any__";
const ANY_ROOM_TYPE = "__any_room__";

export function FiltersBody({
	priceSliderMax,
	sqftSliderMax,
	priceRange,
	setPriceRange,
	sqftRange,
	setSqftRange,
	bedroomFilter,
	setBedroomFilter,
	selectedAmenities,
	toggleAmenity,
	university,
	setUniversity,
	roomTypeFilter,
	setRoomTypeFilter,
	onReset,
}: {
	priceSliderMax: number;
	sqftSliderMax: number;
	priceRange: [number, number];
	setPriceRange: (v: [number, number]) => void;
	sqftRange: [number, number];
	setSqftRange: (v: [number, number]) => void;
	bedroomFilter: number | null;
	setBedroomFilter: (v: number | null) => void;
	selectedAmenities: Set<string>;
	toggleAmenity: (id: string) => void;
	university: string | null;
	setUniversity: (v: string | null) => void;
	roomTypeFilter: string | null;
	setRoomTypeFilter: (v: string | null) => void;
	onReset: () => void;
}) {
	const beds = [1, 2, 3, 4] as const;

	return (
		<div className="min-w-0 space-y-8">
			<div className="space-y-3">
				<h3 className="font-semibold">University</h3>
				<Select
					value={university ?? ANY_UNIVERSITY}
					onValueChange={(v) => setUniversity(v === ANY_UNIVERSITY ? null : v)}
				>
					<SelectTrigger className="h-11 w-full min-w-0 max-w-full">
						{/* Base UI may render the raw `value` for the sentinel; override display text. */}
						<SelectValue placeholder="Any university">
							{university == null ? "Any university" : university}
						</SelectValue>
					</SelectTrigger>
					<SelectContent className="max-w-[calc(100vw-2rem)] sm:max-w-none">
						<SelectItem value={ANY_UNIVERSITY}>Any university</SelectItem>
						{UNIVERSITY_OPTIONS.map((u) => (
							<SelectItem key={u} value={u}>
								{u}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Room type</h3>
				<Select
					value={roomTypeFilter ?? ANY_ROOM_TYPE}
					onValueChange={(v) => setRoomTypeFilter(v === ANY_ROOM_TYPE ? null : v)}
				>
					<SelectTrigger className="h-11 w-full min-w-0 max-w-full">
						<SelectValue placeholder="Any room type">
							{roomTypeFilter == null ? "Any room type" : roomTypeFilter}
						</SelectValue>
					</SelectTrigger>
					<SelectContent className="max-w-[calc(100vw-2rem)] sm:max-w-none">
						<SelectItem value={ANY_ROOM_TYPE}>Any room type</SelectItem>
						{ROOM_TYPE_OPTIONS.map((rt) => (
							<SelectItem key={rt} value={rt}>
								{rt}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Price Range</h3>
				<Slider
					min={0}
					max={priceSliderMax}
					step={50}
					value={priceRange}
					onValueChange={(v) => setPriceRange(v as [number, number])}
				/>
				<div className="flex min-w-0 justify-between gap-2 text-sm text-muted-foreground tabular-nums">
					<span className="min-w-0 shrink truncate">${priceRange[0]}</span>
					<span className="min-w-0 shrink truncate text-right">${priceRange[1]}</span>
				</div>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Square Footage</h3>
				<Slider
					min={0}
					max={sqftSliderMax}
					step={50}
					value={sqftRange}
					onValueChange={(v) => setSqftRange(v as [number, number])}
				/>
				<div className="flex min-w-0 justify-between gap-2 text-sm text-muted-foreground tabular-nums">
					<span className="min-w-0 shrink">{sqftRange[0]} sq ft</span>
					<span className="min-w-0 shrink text-right">{sqftRange[1]} sq ft</span>
				</div>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Bedrooms</h3>
				<div className="flex flex-wrap gap-2">
					{beds.map((n) => (
						<button
							key={n}
							type="button"
							onClick={() => setBedroomFilter(bedroomFilter === n ? null : n)}
							className={cn(
								"min-h-10 rounded-full border px-3 py-2 text-sm transition touch-manipulation sm:min-h-0 sm:py-1.5",
								bedroomFilter === n
									? "border-foreground bg-muted font-medium"
									: "border-input hover:bg-muted/60",
							)}
						>
							{n} bed{n > 1 ? "s" : ""}
						</button>
					))}
				</div>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Amenities</h3>
				<ul className="space-y-3">
					{AMENITY_OPTIONS.map((id) => (
						<li key={id} className="flex min-w-0 items-start gap-3">
							<Checkbox
								id={`amenity-${id}`}
								className="mt-0.5"
								checked={selectedAmenities.has(id)}
								onCheckedChange={() => toggleAmenity(id)}
							/>
							<Label
								htmlFor={`amenity-${id}`}
								className="min-w-0 flex-1 cursor-pointer font-normal leading-snug"
							>
								{id}
							</Label>
						</li>
					))}
				</ul>
			</div>

			<Button type="button" variant="outline" className="w-full" onClick={onReset}>
				Reset filters
			</Button>
		</div>
	);
}
