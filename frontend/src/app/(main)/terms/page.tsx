import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — SubLease",
  description: "Rules for using SubLease.",
};

export default function TermsPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-12 lg:px-8">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Terms of Service</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Last updated: {new Date().toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </header>

      <div className="space-y-6 text-sm leading-relaxed text-foreground">
        <section>
          <h2 className="mb-2 text-lg font-medium">Using SubLease</h2>
          <p className="text-muted-foreground">
            SubLease is a platform where college students can post and browse
            short-term housing listings. By using the site you agree to use it
            in good faith and in compliance with applicable laws.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Your account</h2>
          <p className="text-muted-foreground">
            You are responsible for the accuracy of the information you post,
            for keeping your password secure, and for everything that happens
            under your account.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Listings</h2>
          <p className="text-muted-foreground">
            You may only list housing you have the legal right to sublet or
            rent. SubLease does not verify listings and is not a party to any
            agreement between users. Disputes are between the listing host and
            the renter.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Prohibited conduct</h2>
          <ul className="list-disc space-y-1 pl-5 text-muted-foreground">
            <li>Posting false, misleading, or fraudulent listings.</li>
            <li>Harassing or abusing other users.</li>
            <li>Scraping the site or interfering with normal operation.</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">No warranty</h2>
          <p className="text-muted-foreground">
            The service is provided &quot;as is.&quot; We make no guarantees
            about availability, accuracy, or fitness for a particular purpose.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Changes</h2>
          <p className="text-muted-foreground">
            We may update these terms as the project evolves. Continued use of
            the site after a change means you accept the updated terms.
          </p>
        </section>
      </div>
    </main>
  );
}
