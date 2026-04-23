import Link from "next/link";

export default function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2">
      <span className="text-2xl font-bold text-pink-600">SubLease</span>
    </Link>
  );
}

export function LogoMobile() {
  return (
    <Link href="/" className="flex items-center gap-2">
      <span className="text-xl font-bold text-pink-600">SubLease</span>
    </Link>
  );
}