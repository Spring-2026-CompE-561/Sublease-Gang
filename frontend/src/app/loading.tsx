export default function Loading() {
	return (
	  <main className="container mx-auto flex flex-1 items-center justify-center px-4 py-16">
		<div className="flex flex-col items-center gap-2">
		  <div className="animate-spin h-5 w-5 border-2 border-muted-foreground border-t-transparent rounded-full" />
		  <p className="text-sm text-muted-foreground">Loading...</p>
		</div>
	  </main>
	);
  }