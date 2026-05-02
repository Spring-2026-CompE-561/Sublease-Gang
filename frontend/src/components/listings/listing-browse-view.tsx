"use client";

import { useMemo, useState } from "react";
import { Filter } from "lucide-react";
import {
	AMENITY_OPTIONS,
	filterBrowseListings,
	MOCK_BROWSE_LISTINGS,
	PRICE_FILTER_MAX,
	type BrowseFiltersState,
} from "@/lib/listings";
import { ListingBrowseCard } from "@/components/listings/listing-browse-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import {
	Sheet,
	SheetContent,
	SheetFooter,
	SheetHeader,
	SheetTitle,
	SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

function FiltersBody({
	priceRange,
	setPriceRange,
	bedroomFilter,
	setBedroomFilter,
	selectedAmenities,
	toggleAmenity,
	onReset,
}: {
	priceRange: [number, number];
	setPriceRange: (v: [number, number]) => void;
	bedroomFilter: number | null;
	setBedroomFilter: (v: number | null) => void;
	selectedAmenities: Set<string>;
	toggleAmenity: (id: string) => void;
	onReset: () => void;
}) {
	const beds = [1, 2, 3, 4] as const;

	return (
		<div className="space-y-8">
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

export function ListingBrowseView() {
	const [priceRange, setPriceRange] = useState<[number, number]>([0, PRICE_FILTER_MAX]);
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [mobileOpen, setMobileOpen] = useState(false);

	const filters: BrowseFiltersState = useMemo(
		() => ({
			priceMin: priceRange[0],
			priceMax: priceRange[1],
			bedrooms: bedroomFilter,
			amenities: selectedAmenities,
		}),
		[priceRange, bedroomFilter, selectedAmenities],
	);

	const filtered = useMemo(() => filterBrowseListings(MOCK_BROWSE_LISTINGS, filters), [filters]);

	function toggleAmenity(id: string) {
		setSelectedAmenities((prev) => {
			const next = new Set(prev);
			if (next.has(id)) next.delete(id);
			else next.add(id);
			return next;
		});
	}

	function resetFilters() {
		setPriceRange([0, PRICE_FILTER_MAX]);
		setBedroomFilter(null);
		setSelectedAmenities(new Set());
	}

	const filterProps = {
		priceRange,
		setPriceRange,
		bedroomFilter,
		setBedroomFilter,
		selectedAmenities,
		toggleAmenity,
		onReset: resetFilters,
	};

	return (
		<div className="mx-auto max-w-7xl px-4 pb-12 pt-6 md:px-6 lg:px-8">
			<div className="flex flex-col gap-8 lg:flex-row lg:items-start">
				<aside className="hidden shrink-0 lg:block lg:w-64 xl:w-72">
					<Card className="p-5 shadow-sm ring-foreground/10">
						<h2 className="mb-6 text-lg font-semibold">Filters</h2>
						<FiltersBody {...filterProps} />
					</Card>
				</aside>

				<div className="min-w-0 flex-1">
					<div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
						<div>
							<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">All Listings</h1>
							<p className="mt-1 text-muted-foreground">
								{filtered.length} listing{filtered.length !== 1 ? "s" : ""} available
							</p>
						</div>

						<div className="lg:hidden">
							<Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
								<SheetTrigger
									render={
										<Button variant="outline" className="gap-2 rounded-xl">
											<Filter className="size-4" />
											Filters
										</Button>
									}
								/>
								<SheetContent
									side="left"
									className="flex w-[min(100vw-2rem,380px)] flex-col gap-0 overflow-y-auto"
								>
									<SheetHeader>
										<SheetTitle>Filters</SheetTitle>
									</SheetHeader>
									<div className="flex-1 py-6">
										<FiltersBody {...filterProps} />
									</div>
									<SheetFooter className="border-t pt-4">
										<Button type="button" className="w-full" onClick={() => setMobileOpen(false)}>
											Show results
										</Button>
									</SheetFooter>
								</SheetContent>
							</Sheet>
						</div>
					</div>

					<div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
						{filtered.map((listing) => (
							<ListingBrowseCard key={listing.id} listing={listing} />
						))}
					</div>

					{filtered.length === 0 ? (
						<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
							No listings match these filters. Try adjusting price or amenities.
						</p>
					) : null}
				</div>
			</div>
		</div>
	);
}
