"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
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
import { ListingBrowseCard } from "@/components/listings/listing-browse-card";
import { FiltersBody } from "@/components/listings/filters-body";
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

export function ListingBrowseView() {
	const searchParams = useSearchParams();
	const query = searchParams.get("q") ?? "";
	const [priceRange, setPriceRange] = useState<[number, number]>([0, PRICE_FILTER_MAX]);
	const [sqftRange, setSqftRange] = useState<[number, number]>([0, SQFT_FILTER_MAX]);
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [collegeId, setCollegeId] = useState<number | null>(null);
	const [collegeOptions, setCollegeOptions] = useState<CollegeFilterOption[]>(() => collegeOptionsFromMockListings());
	const [mobileOpen, setMobileOpen] = useState(false);

	const [listings, setListings] = useState<BrowseListing[]>([]);
	const [loading, setLoading] = useState(true);
	const [loadError, setLoadError] = useState<string | null>(null);

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
		let cancelled = false;
		fetchBrowseListings()
			.then((data) => {
				if (!cancelled) setListings(data);
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

	const collegeLabelById = useMemo(() => {
		const m = new Map<number, string>();
		for (const c of collegeOptions) {
			m.set(c.id, c.label);
		}
		return m;
	}, [collegeOptions]);

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

	const filtered = useMemo(() => {
		const base = filterBrowseListings(listings, filters);
		const trimmed = query.trim().toLowerCase();
		if (!trimmed) return base;
		return base.filter((l) => {
			const loc = (l.location ?? "").toLowerCase();
			const uni = (l.university ?? "").toLowerCase();
			const college =
				l.college_id != null
					? (collegeLabelById.get(l.college_id) ?? "").toLowerCase()
					: "";
			return (
				l.title.toLowerCase().includes(trimmed) ||
				loc.includes(trimmed) ||
				uni.includes(trimmed) ||
				college.includes(trimmed)
			);
		});
	}, [collegeLabelById, filters, listings, query]);

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
					</div>

					{loading ? (
						<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
							Loading listings...
						</p>
					) : loadError ? (
						<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
							{loadError}
						</p>
					) : (
						<>
							<div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
								{filtered.map((listing) => (
									<ListingBrowseCard key={listing.id} listing={listing} />
								))}
							</div>

							{listings.length === 0 ? (
								<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
									No listings yet. Check back soon.
								</p>
							) : filtered.length === 0 ? (
								<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
									No listings match these filters. Try adjusting price or amenities.
								</p>
							) : null}
						</>
					)}
				</div>
			</div>
		</div>
	);
}
