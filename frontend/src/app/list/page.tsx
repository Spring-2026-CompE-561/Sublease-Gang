import { Navbar } from "@/components/Navbar";
import Footer from "@/components/Footer";
import Link from "next/link";

export default function ListPlacePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="container mx-auto flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
        <h1 className="text-3xl font-semibold">List your place</h1>
        <p className="mt-3 max-w-md text-sm text-muted-foreground">
          The create-listing form is coming soon. Once it&apos;s ready, you&apos;ll be able
          to post a sublease in a few minutes.
        </p>
        <Link
          href="/"
          className="mt-6 text-sm underline underline-offset-4"
        >
          Back to listings
        </Link>
      </main>
      <Footer />
    </div>
  );
}
