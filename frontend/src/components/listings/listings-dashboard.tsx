"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight, Filter, LayoutGrid, MapPin } from "lucide-react";
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
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

const ListingsMap = dynamic(() => import("@/components/Map"), { ssr: false });

const LISTINGS_PER_PAGE = 12;

type DashboardView = "listings" | "map";

function parseView(value: string | null): DashboardView {
	return value === "map" ? "map" : "listings";
}

export type ListingsDashboardProps = {
	defaultView?: DashboardView;
};

export function ListingsDashboard({ defaultView = "listings" }: ListingsDashboardProps) {
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();
	const query = searchParams.get("q") ?? "";
	const viewParam = searchParams.get("view");
	const view: DashboardView = viewParam ? parseView(viewParam) : defaultView;

	const [priceRange, setPriceRange] = useState<[number, number]>([0, PRICE_FILTER_MAX]);
	const [sqftRange, setSqftRange] = useState<[number, number]>([0, SQFT_FILTER_MAX]);
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [collegeId, setCollegeId] = useState<number | null>(null);
	const [collegeOptions, setCollegeOptions] = useState<CollegeFilterOption[]>([]);
	const [moveIn, setMoveIn] = useState<string | null>(null);
	const [moveOut, setMoveOut] = useState<string | null>(null);
	const [mobileOpen, setMobileOpen] = useState(false);

	const [listings, setListings] = useState<BrowseListing[]>([]);
	const [loading, setLoading] = useState(true);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [currentPage, setCurrentPage] = useState(1);
	const gridRef = useRef<HTMLDivElement>(null);
	const isFirstRender = useRef(true);

	const [flyTo, setFlyTo] = useState<FlyToTarget | undefined>();

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
		fetchBrowseListings({ limit: 100 })
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
				// Permission denied or unavailable — keep the default view.
			},
			{ timeout: 10000 },
		);
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
			moveIn,
			moveOut,
		}),
		[priceRange, sqftRange, bedroomFilter, selectedAmenities, collegeId, moveIn, moveOut],
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

	/* eslint-disable react-hooks/set-state-in-effect -- reset to page 1 when filters change */
	useEffect(() => {
		setCurrentPage(1);
	}, [filters, query]);
	/* eslint-enable react-hooks/set-state-in-effect */

	useEffect(() => {
		if (isFirstRender.current) {
			isFirstRender.current = false;
			return;
		}
		gridRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
	}, [currentPage]);

	const totalPages = Math.max(Math.ceil(filtered.length / LISTINGS_PER_PAGE), 1);
	const safePage = Math.min(currentPage, totalPages);
	const startIndex = (safePage - 1) * LISTINGS_PER_PAGE;
	const paginatedListings = filtered.slice(startIndex, startIndex + LISTINGS_PER_PAGE);

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
		setMoveIn(null);
		setMoveOut(null);
	}

	const setView = useCallback(
		(next: DashboardView) => {
			if (next === view) return;
			const params = new URLSearchParams(searchParams.toString());
			if (next === "listings") {
				params.delete("view");
			} else {
				params.set("view", next);
			}
			const qs = params.toString();
			router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
		},
		[pathname, router, searchParams, view],
	);

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
		moveIn,
		setMoveIn,
		moveOut,
		setMoveOut,
		onReset: resetFilters,
	};

	const resultCount = view === "map" ? pins.length : filtered.length;
	const countLabel = loading
		? "Loading listings..."
		: loadError
			? loadError
			: view === "map"
				? `${resultCount} listing${resultCount !== 1 ? "s" : ""} on the map`
				: `${resultCount} listing${resultCount !== 1 ? "s" : ""} available`;

	return (
		<main className="flex flex-1 flex-col">
			<div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-4 pb-12 pt-6 md:px-6 lg:flex-row lg:items-start lg:gap-8 lg:px-8">
				<aside className="hidden shrink-0 lg:block lg:w-64 xl:w-72">
					<Card className="p-5 shadow-sm ring-foreground/10">
						<h2 className="mb-6 text-lg font-semibold">Filters</h2>
						<FiltersBody {...filterProps} />
					</Card>
				</aside>

				<div className="min-w-0 flex-1">
					<div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
						<div className="flex items-center gap-3">
							<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
								{view === "map" ? "Map" : "All Listings"}
							</h1>
						</div>
						<div className="flex items-center gap-2">
							<ToggleGroup
								value={view}
								onValueChange={(next) => {
									if (next === "listings" || next === "map") setView(next);
								}}
								variant="outline"
								aria-label="Switch between listings and map view"
							>
								<ToggleGroupItem value="listings" aria-label="Listings view">
									<LayoutGrid className="size-4" />
									<span className="hidden sm:inline">Listings</span>
								</ToggleGroupItem>
								<ToggleGroupItem value="map" aria-label="Map view">
									<MapPin className="size-4" />
									<span className="hidden sm:inline">Map</span>
								</ToggleGroupItem>
							</ToggleGroup>
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
					</div>

					<p className="mb-4 text-sm text-muted-foreground">{countLabel}</p>

					{view === "map" ? (
						<div className="h-[calc(100vh-12rem)] w-full overflow-hidden rounded-xl lg:h-[calc(100vh-10rem)]">
							<ListingsMap pins={pins} flyTo={flyTo} />
						</div>
					) : loading ? (
						<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
							Loading listings...
						</p>
					) : loadError ? (
						<p className="rounded-xl border border-dashed py-12 text-center text-muted-foreground">
							{loadError}
						</p>
					) : (
						<>
							<div ref={gridRef} className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
								{paginatedListings.map((listing) => (
									<ListingBrowseCard key={listing.id} listing={listing} />
								))}
							</div>

							{filtered.length > 0 && totalPages > 1 && (
								<div className="mt-8 flex items-center justify-center gap-2">
									<Button
										variant="outline"
										size="sm"
										onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
										disabled={safePage === 1}
										className="gap-1"
									>
										<ChevronLeft className="size-4" />
										Previous
									</Button>
									<div className="flex gap-1">
										{Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
											<Button
												key={page}
												variant={safePage === page ? "default" : "outline"}
												size="sm"
												onClick={() => setCurrentPage(page)}
												className="min-w-10"
											>
												{page}
											</Button>
										))}
									</div>
									<Button
										variant="outline"
										size="sm"
										onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
										disabled={safePage === totalPages}
										className="gap-1"
									>
										Next
										<ChevronRight className="size-4" />
									</Button>
								</div>
							)}

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
		</main>
	);
}
