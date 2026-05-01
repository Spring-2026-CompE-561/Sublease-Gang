import Logo from "@/components/Logo";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <div className="border-b bg-background">
        <nav className="mx-auto flex h-20 w-full max-w-7xl items-center justify-center px-6 lg:px-8">
          <Logo />
        </nav>
      </div>
      {children}
    </>
  );
}