"use client";

import Logo from "@/components/Logo";
import Link from "next/link";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useState } from "react";
import { Menu, Search, User } from "lucide-react";

export function Navbar() {
  return (
    <>
      <DesktopNavbar />
      <MobileNavbar />
    </>
  );
}

function DesktopNavbar() {
  return (
    <div className="hidden border-b bg-background md:block">
      <nav className="container flex h-20 items-center justify-between px-8">
        <Logo />

        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by location, university..."
            className="pl-9 rounded-full bg-muted"
          />
        </div>

        <div className="flex items-center gap-4">
          <Link href="/list" className="text-sm">
            List your place
          </Link>
          <Link
            href="/signin"
            aria-label="Sign in"
            className={buttonVariants({ variant: "ghost", size: "icon" })}
          >
            <User />
          </Link>
        </div>
      </nav>
    </div>
  );
}

function MobileNavbar() {
  const [isOpen, setIsOpen] = useState(false);
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
              <div className="flex flex-col gap-2 pt-6">
                <Link href="/list" onClick={() => setIsOpen(false)}>
                  List your place
                </Link>
                <Link href="/signin" onClick={() => setIsOpen(false)}>
                  Sign in
                </Link>
              </div>
            </div>
          </SheetContent>
        </Sheet>

        <Logo />

        <Button variant="ghost" size="icon">
          <User />
        </Button>
      </nav>
    </div>
  );
}