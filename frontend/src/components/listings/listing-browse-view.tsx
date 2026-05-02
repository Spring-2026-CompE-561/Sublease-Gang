"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Filter } from "lucide-react";
import {
	filterBrowseListings,
	MOCK_BROWSE_LISTINGS,
	PRICE_FILTER_MAX,
	type BrowseFiltersState,
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
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [university, setUniversity] = useState<string | null>(null);
	const [mobileOpen, setMobileOpen] = useState(false);
	

	const filters: BrowseFiltersState = useMemo(
		() => ({
			priceMin: priceRange[0],
			priceMax: priceRange[1],
			bedrooms: bedroomFilter,
			amenities: selectedAmenities,
			university,
		}),
		[priceRange, bedroomFilter, selectedAmenities, university],
	);

	const filtered = useMemo(() => {
  		const base = filterBrowseListings(MOCK_BROWSE_LISTINGS, filters);
  		const trimmed = query.trim().toLowerCase();
  		if (!trimmed) return base;
  			return base.filter(
    	(l) =>
      	l.title.toLowerCase().includes(trimmed) ||
      	l.location.toLowerCase().includes(trimmed) ||
      	l.university.toLowerCase().includes(trimmed),
  		);
	}, [filters, query]);

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
		setUniversity(null);
	}

	const filterProps = {
		priceRange,
		setPriceRange,
		bedroomFilter,
		setBedroomFilter,
		selectedAmenities,
		toggleAmenity,
		university,
		setUniversity,
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
								<SheetContent side="left" className="flex w-[min(100vw-2rem,380px)] flex-col gap-0 overflow-y-auto">
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
