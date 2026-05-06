import Link from "next/link";
import { Separator } from "@/components/ui/separator";

const primaryLinks = [
  { href: "/listings", label: "Browse" },
  { href: "/list", label: "List your place" },
  { href: "/about", label: "About" },
];

const legalLinks = [
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
];

const linkClass =
  "rounded-sm transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background";

export default function Footer() {
  return (
    <footer className="mt-auto bg-background">
      <Separator />
      <div className="mx-auto flex w-full max-w-7xl flex-col items-center gap-4 px-6 py-6 text-sm text-muted-foreground md:flex-row md:justify-between lg:px-8">
        <p>&copy; {new Date().getFullYear()} SubLease</p>
        <nav className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2">
          {primaryLinks.map((link) => (
            <Link key={link.href} href={link.href} className={linkClass}>
              {link.label}
            </Link>
          ))}
        </nav>
        <nav className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-xs">
          {legalLinks.map((link) => (
            <Link key={link.href} href={link.href} className={linkClass}>
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
