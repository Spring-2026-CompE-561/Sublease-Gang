"use client";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User } from "lucide-react";
import { useRouter } from "next/navigation";

import { clearTokens, useIsAuthenticated } from "@/lib/auth";

function UserButton() {
  const router = useRouter();
  const isLoggedIn = useIsAuthenticated();

  function handleSignOut() {
    clearTokens();
    router.push("/");
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" />}>
        <User />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {isLoggedIn ? (
        <>
        <DropdownMenuItem onClick={() => router.push("/profile")}>
        Profile
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => router.push("/saved-listings")}>
        Saved listings
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => router.push("/reported-listings")}>
        Reported listings
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleSignOut}>Sign out</DropdownMenuItem>
        </>
        ) : (
          <>
            <DropdownMenuItem onClick={() => router.push("/signin")}>
              Sign in
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push("/signup")}>
              Sign up
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default UserButton;