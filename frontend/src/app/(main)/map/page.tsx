"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { Filter } from "lucide-react";
import { PRICE_FILTER_MAX } from "@/lib/listings";
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

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const SAMPLE_PINS = [
	{ id: "1", latitude: 32.8801, longitude: -117.234 },
	{ id: "2", latitude: 32.7503, longitude: -117.1859 },
	{ id: "3", latitude: 32.7157, longitude: -117.1611 },
];

export default function MapPage() {
	const [priceRange, setPriceRange] = useState<[number, number]>([0, PRICE_FILTER_MAX]);
	const [bedroomFilter, setBedroomFilter] = useState<number | null>(null);
	const [selectedAmenities, setSelectedAmenities] = useState<Set<string>>(new Set());
	const [mobileOpen, setMobileOpen] = useState(false);

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

					<div className="h-[calc(100vh-9rem)] w-full overflow-hidden rounded-xl lg:h-[calc(100vh-7rem)]">
						<Map pins={SAMPLE_PINS} />
					</div>
				</div>
			</div>
		</main>
	);
}
