import Image from "next/image";

import { Navbar } from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className = "flex min-h-screen flex-col">
      <main className = "flex-1" />
      <Footer />
    </div>
  );
}
