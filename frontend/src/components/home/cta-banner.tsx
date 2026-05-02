import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function CtaBanner() {
  return (
    <section className="bg-slate-900 text-white px-4 py-16">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-3xl font-bold sm:text-4xl">
          Ready to list your place?
        </h2>
        <p className="mt-4 text-base text-slate-300 sm:text-lg">
          Going away for the summer? Make extra income by subletting your apartment to fellow students.
        </p>
        <div className="mt-8 flex justify-center">
          <Button
            nativeButton={false}          
            size="lg"
            variant="secondary"
            render={<Link href="/list">Get Started</Link>}
          />
        </div>
      </div>
    </section>
  );
}