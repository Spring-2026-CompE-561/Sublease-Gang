"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ErrorPage({
	error,
	reset,
}: {
	error: Error & { digest?: string };
	reset: () => void;
}) {
	useEffect(() => {
		console.error(error);
	}, [error]);

	return (
		<main className="container mx-auto flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
			<h1 className="text-2xl font-semibold">Something went wrong</h1>
			<p className="mt-3 text-sm text-muted-foreground">
				An unexpected error happened. Try again or head back home.
			</p>
			<div className="mt-6 flex gap-3">
				<Button variant="outline" onClick={reset}>
					Try again
				</Button>
				<Button onClick={() => (window.location.href = "/")}>Home</Button>
			</div>
		</main>
	);
}
