import Footer from "@/components/Footer";
import Logo from "@/components/Logo";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-svh flex-col">
      <div className="border-b bg-background">
        <nav className="mx-auto flex h-20 w-full max-w-7xl items-center justify-center px-6 lg:px-8">
          <Logo />
        </nav>
      </div>
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center p-6 md:p-10">
        {children}
      </div>
      <Footer />
    </div>
  );
}