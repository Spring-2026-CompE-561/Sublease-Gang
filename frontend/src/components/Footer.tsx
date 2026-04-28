import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-auto border-t bg-background py-6 text-sm text-muted-foreground">
      <div className="container mx-auto flex flex-col items-center justify-between gap-3 px-4 md:flex-row">
        <p>&copy; {new Date().getFullYear()} SubLease</p>
        <nav className="flex gap-4">
          <Link href="/about" className="hover:text-foreground">About</Link>
          <Link href="/list" className="hover:text-foreground">List your place</Link>
          <Link href="/signin" className="hover:text-foreground">Sign in</Link>
        </nav>
      </div>
    </footer>
  );
}
