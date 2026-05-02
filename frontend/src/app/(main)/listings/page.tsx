import { ListingBrowseView } from "@/components/listings/listing-browse-view";

type Props = {
  searchParams: Promise<{ q?: string }>;
};

export default async function AllListingsPage({ searchParams }: Props) {
  const { q } = await searchParams;
  return (
    <main className="flex-1">
      <ListingBrowseView initialQuery={q ?? ""} />
    </main>
  );
}