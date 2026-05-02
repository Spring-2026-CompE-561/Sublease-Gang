"use client";

import {
	AMENITY_OPTIONS,
	PRICE_FILTER_MAX,
	SQFT_FILTER_MAX,
	UNIVERSITY_OPTIONS,
} from "@/lib/listings";
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

export function FiltersBody({
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
	onReset,
}: {
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
	onReset: () => void;
}) {
	const beds = [1, 2, 3, 4] as const;

	return (
		<div className="space-y-8">
			<div className="space-y-3">
				<h3 className="font-semibold">University</h3>
				<Select
					value={university}
					onValueChange={(v) => setUniversity((v as string) || null)}
				>
					<SelectTrigger className="w-full">
						<SelectValue placeholder="Any university" />
					</SelectTrigger>
					<SelectContent>
						{UNIVERSITY_OPTIONS.map((u) => (
							<SelectItem key={u} value={u}>
								{u}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Price Range</h3>
				<Slider
					min={0}
					max={PRICE_FILTER_MAX}
					step={50}
					value={priceRange}
					onValueChange={(v) => setPriceRange(v as [number, number])}
				/>
				<div className="flex justify-between text-sm text-muted-foreground">
					<span>${priceRange[0]}</span>
					<span>${priceRange[1]}</span>
				</div>
			</div>

			<div className="space-y-3">
				<h3 className="font-semibold">Square Footage</h3>
				<Slider
					min={0}
					max={SQFT_FILTER_MAX}
					step={50}
					value={sqftRange}
					onValueChange={(v) => setSqftRange(v as [number, number])}
				/>
				<div className="flex justify-between text-sm text-muted-foreground">
					<span>{sqftRange[0]} sq ft</span>
					<span>{sqftRange[1]} sq ft</span>
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
								"rounded-full border px-3 py-1.5 text-sm transition",
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
						<li key={id} className="flex items-center gap-3">
							<Checkbox
								id={`amenity-${id}`}
								checked={selectedAmenities.has(id)}
								onCheckedChange={() => toggleAmenity(id)}
							/>
							<Label htmlFor={`amenity-${id}`} className="cursor-pointer font-normal leading-none">
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
