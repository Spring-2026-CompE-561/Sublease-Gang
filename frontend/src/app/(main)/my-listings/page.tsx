"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";

export default function MyListingsPage() {
	const router = useRouter();
	const [isAuthorized, setIsAuthorized] = useState(false);

	useEffect(() => {
		const token = localStorage.getItem("access_token");
		if (!token) {
			router.push("/signin");
			return;
		}
		setIsAuthorized(true);
	}, [router]);

	if (!isAuthorized) {
		return (
			<main className="flex-1 px-4 py-16 text-center">
				<p className="text-muted-foreground">Redirecting to sign in...</p>
			</main>
		);
	}

	return (
		<main className="flex-1">
			<div className="border-b bg-background">
				<div className="mx-auto max-w-7xl px-4 py-6 md:px-6">
					<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">My Listings</h1>
					<p className="mt-1 text-sm text-muted-foreground">0 active listings</p>
				</div>
			</div>

			<div className="mx-auto max-w-7xl px-4 py-8 md:px-6">
				<Card className="flex flex-col items-center justify-center gap-3 py-16">
					<p className="text-lg font-medium text-foreground">No listings yet</p>
					<p className="text-sm text-muted-foreground">
						Post a sublease to start hosting students.
					</p>
				</Card>
			</div>
		</main>
	);
}
