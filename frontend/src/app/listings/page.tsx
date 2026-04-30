import Link from "next/link";
import { FilterPanel, MobileFilterSheet } from "@/components/FilterPanel";
import { Filter } from "lucide-react";

export default function ListingPlacePage() {
  return (      
    <div className="flex gap-6">
        <aside className="hidden lg:block w-60 ml-4">
            <FilterPanel />
        </aside>

        <div className="lg:hidden">
            <MobileFilterSheet />
        </div>

        <main className="container mx-auto flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
            <h1 className="text-3xl font-semibold">View Listings</h1>
        </main>
    </div>
  );
}
