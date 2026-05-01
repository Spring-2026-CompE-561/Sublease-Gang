import Hero from "@/components/home/Hero";
import CtaBanner from "@/components/home/cta-banner";

export default function Home() {
  //return null;
  return (
    <main className="flex-1">
      <Hero />
      <CtaBanner />    
    </main>
    );
}
