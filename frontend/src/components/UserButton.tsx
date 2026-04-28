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
import { useState } from "react";

function UserButton() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(() =>
  typeof window !== "undefined" && Boolean(localStorage.getItem("access_token"))
);
  function handleSignOut() {
    localStorage.removeItem("access_token");
    setIsLoggedIn(false);
    router.push("/");
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" />}>
        <User />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {isLoggedIn ? (
          <DropdownMenuItem onClick={handleSignOut}>Sign out</DropdownMenuItem>
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