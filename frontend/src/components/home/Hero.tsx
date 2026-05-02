import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Hero() {
  return (
    <section className="bg-orange-50 dark:bg-orange-950/20 px-4 py-20">
      <div className="mx-auto max-w-3xl text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          Find your perfect student sublease
        </h1>
        <p className="mt-6 text-base text-muted-foreground sm:text-lg">
          Connect with verified students for short-term housing near your campus
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Button
            nativeButton={false}
            size="lg"
            render={<Link href="/listings">Browse Listings</Link>}
          />
          <Button
            nativeButton={false}
            variant="outline"
            size="lg"
            render={<Link href="/list">List Your Place</Link>}
          />
        </div>
      </div>
    </section>
  );
}