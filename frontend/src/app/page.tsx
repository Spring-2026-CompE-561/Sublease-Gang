import Hero from "@/components/home/Hero";
import Features from "@/components/home/features";
import CtaBanner from "@/components/home/cta-banner";

export default function Home() {
  return (
    <main className="flex-1">
      <Hero />
      <Features />
      <CtaBanner />    
    </main>
  );
}