import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — SubLease",
  description: "How SubLease handles your data.",
};

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-12 lg:px-8">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Privacy Policy</h1>
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
          <h2 className="mb-2 text-lg font-medium">What we collect</h2>
          <ul className="list-disc space-y-1 pl-5 text-muted-foreground">
            <li>Account info you provide: email, username, name, profile description.</li>
            <li>Listings you post: title, description, price, location, photos.</li>
            <li>Messages you send to other users on the platform.</li>
            <li>Basic technical data your browser sends (IP, user agent) for normal site operation.</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">How we use it</h2>
          <p className="text-muted-foreground">
            To run the service: showing your listings to other users, letting
            you sign in, and delivering messages. We do not sell your data.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Your choices</h2>
          <p className="text-muted-foreground">
            You can edit or delete your listings and profile at any time.
            Deleting your account removes your listings and profile from the
            site.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Contact</h2>
          <p className="text-muted-foreground">
            Questions about this policy? Reach out through the project&apos;s
            GitHub repository.
          </p>
        </section>
      </div>
    </main>
  );
}
