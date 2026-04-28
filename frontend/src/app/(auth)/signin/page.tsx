import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Sign in coming soon. Authentication isn&apos;t wired up yet.
        </p>
        <p className="text-sm">
          <Link href="/" className="underline underline-offset-4">
            Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}
