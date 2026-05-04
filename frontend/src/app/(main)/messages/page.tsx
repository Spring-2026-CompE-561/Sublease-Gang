import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import { MessagesView } from "./messages-view";

function MessagesFallback() {
	return (
		<main className="container mx-auto flex flex-1 items-center justify-center px-4 py-16">
			<p className="flex items-center gap-2 text-sm text-muted-foreground">
				<Loader2 className="size-4 animate-spin" aria-hidden />
				Loading messages…
			</p>
		</main>
	);
}

export default function MessagesPage() {
	return (
		<Suspense fallback={<MessagesFallback />}>
			<MessagesView />
		</Suspense>
	);
}
