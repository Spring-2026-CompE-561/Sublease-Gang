"use client";

import Logo from "@/components/Logo";
import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useState } from "react";
import {
  LayoutGrid,
  MapPin,
  Menu,
  MessageCircle,
  PlusSquare,
  Search,
} from "lucide-react";
import { ModeToggle } from "@/components/mode-toggle";
import UserButton from "@/components/UserButton";
import { useRouter } from "next/navigation";

export function Navbar() {
  return (
    <>
      <DesktopNavbar />
      <MobileNavbar />
    </>
  );
}

function NavIconLink({
  href,
  label,
  children,
}: {
  href: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <Link
            href={href}
            aria-label={label}
            className={buttonVariants({ variant: "ghost", size: "icon" })}
          >
            {children}
          </Link>
        }
      />
      <TooltipContent>{label}</TooltipContent>
    </Tooltip>
  );
}

function DesktopNavbar() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.push(`/listings?q=${encodeURIComponent(trimmed)}`);
    setQuery("");
  }

  return (
    <div className="hidden border-b bg-background md:block">
      <nav className="mx-auto flex h-20 w-full max-w-7xl items-center gap-6 px-6 lg:px-8">
        <div className="shrink-0">
          <Logo />
        </div>

        <form onSubmit={handleSubmit} className="relative mx-auto w-full max-w-xl flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by location, university..."
            className="pl-9 rounded-full bg-muted"
          />
        </form>

        <div className="flex shrink-0 items-center gap-1">
          <NavIconLink href="/listings" label="Browse">
            <LayoutGrid className="h-5 w-5" />
          </NavIconLink>
          <NavIconLink href="/map" label="Map">
            <MapPin className="h-5 w-5" />
          </NavIconLink>
          <NavIconLink href="/list" label="List your place">
            <PlusSquare className="h-5 w-5" />
          </NavIconLink>
          <NavIconLink href="/messages" label="Messages">
            <MessageCircle className="h-5 w-5" />
          </NavIconLink>
          <ModeToggle />
          <UserButton />
        </div>
      </nav>
    </div>
  );
}

function MobileNavbar() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.push(`/listings?q=${encodeURIComponent(trimmed)}`);
    setQuery("");
    setIsOpen(false);
  }

  return (
    <div className="block border-b bg-background md:hidden">
      <nav className="container flex h-16 items-center justify-between px-4">
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetTrigger render={<Button variant="ghost" size="icon" />}>
            <Menu />
          </SheetTrigger>
          <SheetContent side="left" className="w-80">
            <div className="pt-4">
              <Logo />

              <form onSubmit={handleSubmit} className="relative mt-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by location, university..."
                  className="pl-9 rounded-full bg-muted"
                />
              </form>

              <div className="flex flex-col gap-2 pt-6">
                <Link href="/listings" onClick={() => setIsOpen(false)}>
                  Browse listings
                </Link>
                <Link href="/map" onClick={() => setIsOpen(false)}>
                  Map
                </Link>
                <Link href="/list" onClick={() => setIsOpen(false)}>
                  List your place
                </Link>
                <Link href="/messages" onClick={() => setIsOpen(false)}>
                  Messages
                </Link>
              </div>
            </div>
          </SheetContent>
        </Sheet>

        <Logo />

        <div className="flex items-center gap-2">
          <ModeToggle />
          <UserButton />
        </div>
      </nav>
    </div>
  );
}