import Hero from "@/components/home/Hero";
import Features from "@/components/home/features";
import CtaBanner from "@/components/home/cta-banner";
import { ListingCard } from "@/components/ListingCard";
import { fetchBrowseListings, type BrowseListing } from "@/lib/listings";

export default async function Home() {
  let featuredListings: BrowseListing[] = [];
  let loadFailed = false;
  try {
    const response = await fetchBrowseListings({ limit: 4 });
    featuredListings = response.results;
  } catch (e) {
    console.error("home featured fetch failed", e);
    loadFailed = true;
  }

  return (
    <main className="flex-1">
      <Hero />
      <Features />
      <section className="container mx-auto px-4 py-12">
        <h2 className="mb-6 text-2xl font-semibold">Available subleases</h2>
        {loadFailed ? (
          <p className="text-sm text-muted-foreground">
            Could not load listings right now. Please try again later.
          </p>
        ) : featuredListings.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No listings yet. Check back soon.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {featuredListings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>
      <CtaBanner />
    </main>
  );
}
