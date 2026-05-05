"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchSavedListings } from "@/lib/listings";
import type { BrowseListing } from "@/lib/listings";
import { ListingBrowseCard } from "@/components/listings/listing-browse-card";
import { Card } from "@/components/ui/card";
import { ACCESS_TOKEN_KEY } from "@/lib/api";

export default function SavedListingsPage() {
  const router = useRouter();
  const [isAuthorized] = useState(() =>
    typeof window !== "undefined" && !!localStorage.getItem(ACCESS_TOKEN_KEY)
  );
  const [listings, setListings] = useState<BrowseListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

useEffect(() => {
  if (!isAuthorized) {
    router.push("/signin");
  }
}, [isAuthorized, router]);

  useEffect(() => {
    if (!isAuthorized) return;

    let cancelled = false;
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) return;

    fetchSavedListings(token)
      .then((data) => {
        if (!cancelled) setListings(data);
      })
      .catch((e) => {
        console.error("fetchSavedListings", e);
        if (!cancelled) setLoadError("Could not load saved listings.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthorized]);

  if (!isAuthorized) {
    return (
      <main className="flex-1 px-4 py-16 text-center">
        <p className="text-muted-foreground">Redirecting to sign in...</p>
      </main>
    );
  }

  return (
    <main className="flex-1">
      <div className="border-b bg-background">
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-6">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Saved Listings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {listings.length} listing{listings.length !== 1 ? "s" : ""} saved
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 md:px-6">
        {loading ? (
          <Card className="flex flex-col items-center justify-center gap-3 py-16">
            <p className="text-sm text-muted-foreground">Loading saved listings...</p>
          </Card>
        ) : loadError ? (
          <Card className="flex flex-col items-center justify-center gap-3 py-16">
            <p className="text-lg font-medium text-foreground">Error loading saved listings</p>
            <p className="text-sm text-muted-foreground">{loadError}</p>
          </Card>
        ) : listings.length > 0 ? (
          <div className="grid auto-rows-max gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {listings.map((listing) => (
              <ListingBrowseCard key={listing.id} listing={listing} from="saved-listings" />
            ))}
          </div>
        ) : (
          <Card className="flex flex-col items-center justify-center gap-3 py-16">
            <p className="text-lg font-medium text-foreground">No saved listings yet</p>
            <p className="text-sm text-muted-foreground">
              Browse listings and save your favorites to see them here
            </p>
          </Card>
        )}
      </div>
    </main>
  );
}