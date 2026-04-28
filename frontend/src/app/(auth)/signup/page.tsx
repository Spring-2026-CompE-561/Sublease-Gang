import Link from "next/link";

export default function SignUpPage() {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-semibold">Create an account</h1>
        <p className="text-sm text-muted-foreground">
          Sign up coming soon. Authentication isn&apos;t wired up yet.
        </p>
        <p className="text-sm">
          Already have one?{" "}
          <Link href="/signin" className="underline underline-offset-4">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
