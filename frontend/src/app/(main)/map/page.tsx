"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { Filter } from "lucide-react";
import {
	collegeOptionsFromMockListings,
	fetchBrowseListings,
	fetchCollegeFilterOptions,
	filterBrowseListings,
	PRICE_FILTER_MAX,
	SQFT_FILTER_MAX,
	type BrowseFiltersState,
	type BrowseListing,
	type CollegeFilterOption,
} from "@/lib/listings";
import { FiltersBody } from "@/components/listings/filters-body";
import type { FlyToTarget } from "@/components/Map";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
	Sheet,
	SheetContent,
	SheetFooter,
	SheetHeader,
	SheetTitle,
	SheetTrigger,
} from "@/components/ui/sheet";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

export default function MapPage() {
	const [priceRange, setPriceRange] = useState<[number, number]>([0, PRICE_FILTER_MAX]);
	const [sqftRange, setSqftRange] = useState<[number, number]>([0, SQFT_FILTER_MAX]);
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [collegeId, setCollegeId] = useState<number | null>(null);
	const [mobileOpen, setMobileOpen] = useState(false);
	const [flyTo, setFlyTo] = useState<FlyToTarget | undefined>();
	const [listings, setListings] = useState<BrowseListing[]>([]);
	const [loading, setLoading] = useState(true);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [collegeOptions, setCollegeOptions] = useState<CollegeFilterOption[]>([]);

	useEffect(() => {
		let cancelled = false;
		fetchBrowseListings()
			.then((response) => {
				if (!cancelled) setListings(response.results);
			})
			.catch((e) => {
				console.error("fetchBrowseListings", e);
				if (!cancelled) setLoadError("Could not load listings.");
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		let cancelled = false;
		fetchCollegeFilterOptions()
			.then((opts) => {
				if (!cancelled) setCollegeOptions(opts);
			})
			.catch(() => {
				if (!cancelled) setCollegeOptions(collegeOptionsFromMockListings());
			});
		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		if (typeof window === "undefined" || !("geolocation" in navigator)) return;
		navigator.geolocation.getCurrentPosition(
			(pos) => {
				setFlyTo({
					latitude: pos.coords.latitude,
					longitude: pos.coords.longitude,
					zoom: 12,
				});
			},
			() => {
				// Permission denied or unavailable — keep the default San Diego view.
			},
			{ timeout: 10000 },
		);
	}, []);

	const filters: BrowseFiltersState = useMemo(
		() => ({
			priceMin: priceRange[0],
			priceMax: priceRange[1],
			sqftMin: sqftRange[0],
			sqftMax: sqftRange[1],
			bedrooms: bedroomFilter,
			amenities: selectedAmenities,
			collegeId,
		}),
		[priceRange, sqftRange, bedroomFilter, selectedAmenities, collegeId],
	);

	const filtered = useMemo(
		() => filterBrowseListings(listings, filters),
		[listings, filters],
	);

	const pins = useMemo(
		() =>
			filtered
				.filter((l) => l.latitude !== 0 || l.longitude !== 0)
				.map((l) => ({
					id: String(l.id),
					latitude: l.latitude,
					longitude: l.longitude,
					title: l.title,
					price: l.price,
					thumbnailUrl: l.thumbnail_url ?? undefined,
					location: l.location,
				})),
		[filtered],
	);

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
		setSqftRange([0, SQFT_FILTER_MAX]);
		setBedroomFilter(null);
		setSelectedAmenities(new Set());
		setCollegeId(null);
	}

	const filterProps = {
		priceRange,
		setPriceRange,
		sqftRange,
		setSqftRange,
		bedroomFilter,
		setBedroomFilter,
		selectedAmenities,
		toggleAmenity,
		collegeId,
		setCollegeId,
		collegeOptions,
		onReset: resetFilters,
	};

	return (
		<main className="flex flex-1 flex-col">
			<div className="flex flex-col gap-4 px-4 pt-6 md:px-6 lg:flex-row lg:items-start lg:gap-8 lg:px-8">
				<aside className="hidden shrink-0 lg:block lg:w-64 xl:w-72">
					<Card className="p-5 shadow-sm ring-foreground/10">
						<h2 className="mb-6 text-lg font-semibold">Filters</h2>
						<FiltersBody {...filterProps} />
					</Card>
				</aside>

				<div className="min-w-0 flex-1">
					<div className="mb-4 flex items-center justify-between lg:hidden">
						<h1 className="text-xl font-semibold tracking-tight">Map</h1>
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
								className="flex h-dvh max-h-dvh w-[min(100vw-1rem,24rem)] flex-col gap-0 overflow-hidden border-r p-0"
							>
								<SheetHeader className="shrink-0 space-y-0 border-b px-4 pb-4 pt-6">
									<SheetTitle>Filters</SheetTitle>
								</SheetHeader>
								<div className="min-h-0 flex-1 overflow-y-auto overscroll-y-contain px-4 py-4 [-webkit-overflow-scrolling:touch]">
									<FiltersBody {...filterProps} />
								</div>
								<SheetFooter className="shrink-0 gap-2 border-t bg-background/95 px-4 pt-4 pb-[max(1rem,env(safe-area-inset-bottom))] backdrop-blur-sm supports-backdrop-filter:bg-background/80">
									<Button type="button" className="w-full" onClick={() => setMobileOpen(false)}>
										Show results
									</Button>
								</SheetFooter>
							</SheetContent>
						</Sheet>
					</div>

					<p className="mb-2 text-sm text-muted-foreground">
						{loading
							? "Loading listings..."
							: loadError
								? loadError
								: `${pins.length} listing${pins.length !== 1 ? "s" : ""} on the map`}
					</p>

					<div className="h-[calc(100vh-9rem)] w-full overflow-hidden rounded-xl lg:h-[calc(100vh-7rem)]">
						<Map pins={pins} flyTo={flyTo} />
					</div>
				</div>
			</div>
		</main>
	);
}
