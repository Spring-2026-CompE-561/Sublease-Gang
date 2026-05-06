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

import { signOut, useIsAuthenticated } from "@/lib/auth";

function UserButton() {
  const router = useRouter();
  const isLoggedIn = useIsAuthenticated();

  async function handleSignOut() {
    await signOut();
    router.push("/");
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" />}>
        <User />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="center" className="w-auto min-w-0">
        {isLoggedIn ? (
          <>
            <DropdownMenuItem
              onClick={() => router.push("/profile")}
              className="justify-center px-4"
            >
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => router.push("/my-listings")}
              className="justify-center px-4"
            >
              My Listings
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => router.push("/saved-listings")}
              className="justify-center px-4"
            >
              Saved listings
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={handleSignOut}
              className="justify-center px-4"
            >
              Sign out
            </DropdownMenuItem>
          </>
        ) : (
          <>
            <DropdownMenuItem
              onClick={() => router.push("/signin")}
              className="justify-center px-4"
            >
              Sign in
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => router.push("/signup")}
              className="justify-center px-4"
            >
              Sign up
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default UserButton;