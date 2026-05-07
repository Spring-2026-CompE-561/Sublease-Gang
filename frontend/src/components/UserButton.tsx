"use client";

import Link from "next/link";
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

  if (!isLoggedIn) {
    return (
      <div className="flex items-center gap-2">
        <Button
          nativeButton={false}
          variant="ghost"
          size="sm"
          render={<Link href="/signin">Sign in</Link>}
        />
        <Button
          nativeButton={false}
          size="sm"
          render={<Link href="/signup">Sign up</Link>}
        />
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" />}>
        <User />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="center" className="w-auto min-w-0">
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
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default UserButton;
