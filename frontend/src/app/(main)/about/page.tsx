import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About — SubLease",
  description:
    "SubLease is a student-built marketplace for short-term college housing, created for CompE 561.",
};

const REPO_URL = "https://github.com/Spring-2026-CompE-561/Sublease-Gang";

type Contributor = {
  name: string;
  handle: string;
  avatarUrl: string;
};

const TEAM: Contributor[] = [
  {
    name: "Jaden Ong",
    handle: "jadengong",
    avatarUrl: "https://avatars.githubusercontent.com/u/171640604?v=4",
  },
  {
    name: "Caleb Dickson",
    handle: "CalebDksn25",
    avatarUrl: "https://avatars.githubusercontent.com/u/157729906?v=4",
  },
  {
    name: "Dean Kajosevic",
    handle: "deankajosevic",
    avatarUrl: "https://avatars.githubusercontent.com/u/118306845?v=4",
  },
  {
    name: "Benjamin Dennis",
    handle: "bendennis06",
    avatarUrl: "https://avatars.githubusercontent.com/u/130309802?v=4",
  },
  {
    name: "Enzo Weiss",
    handle: "enzoweiss21",
    avatarUrl: "https://avatars.githubusercontent.com/u/178350078?v=4",
  },
];

export default function AboutPage() {
  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-12 lg:px-8">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">About SubLease</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          A student-built marketplace for short-term college housing.
        </p>
      </header>

      <div className="space-y-10 text-sm leading-relaxed text-foreground">
        <section>
          <h2 className="mb-2 text-lg font-medium">The project</h2>
          <p className="text-muted-foreground">
            SubLease was built as a semester project for{" "}
            <span className="font-medium text-foreground">CompE 561</span>. There&apos;s
            no central place for college students to list or find subleases, so
            we set out to make one: a simple, focused site where students near a
            campus can post a room and others can browse, filter, and message
            them directly.
          </p>
          <p className="mt-3 text-muted-foreground">
            The site is intentionally limited to matching renters with available
            rooms. Payment, lease signing, and verification are left to the
            people involved.
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">What we built</h2>
          <ul className="list-disc space-y-1 pl-5 text-muted-foreground">
            <li>Listings with photos, price, room size, and date range.</li>
            <li>Account sign-up and sign-in with secure password hashing.</li>
            <li>Filtering by college, time frame, room size, and price.</li>
            <li>A map view showing where listings are located.</li>
            <li>Direct messaging between renters and hosts.</li>
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Tech stack</h2>
          <p className="text-muted-foreground">
            Next.js, React, and Tailwind on the frontend. FastAPI, SQLAlchemy,
            and Python on the backend. The full stack and architecture notes
            live in the project README.
          </p>
        </section>

        <section>
          <h2 className="mb-4 text-lg font-medium">The team</h2>
          <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {TEAM.map((person) => (
              <li
                key={person.handle}
                className="flex items-center gap-4 rounded-lg border border-border/60 bg-card/40 p-4"
              >
                <Image
                  src={person.avatarUrl}
                  alt={`${person.name} (@${person.handle})`}
                  width={56}
                  height={56}
                  className="h-14 w-14 shrink-0 rounded-full object-cover"
                  unoptimized
                />
                <div className="min-w-0">
                  <p className="truncate font-medium text-foreground">
                    {person.name}
                  </p>
                  <Link
                    href={`https://github.com/${person.handle}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="truncate text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                  >
                    @{person.handle}
                  </Link>
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted-foreground">
            Full contributor history is available on{" "}
            <Link
              href={`${REPO_URL}/graphs/contributors`}
              target="_blank"
              rel="noopener noreferrer"
              className="underline-offset-4 hover:text-foreground hover:underline"
            >
              GitHub
            </Link>
            .
          </p>
        </section>

        <section>
          <h2 className="mb-2 text-lg font-medium">Source code</h2>
          <p className="text-muted-foreground">
            SubLease is open source. Browse the code, file issues, or open a
            pull request on{" "}
            <Link
              href={REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-foreground underline-offset-4 hover:underline"
            >
              GitHub
            </Link>
            .
          </p>
        </section>
      </div>
    </main>
  );
}
