"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";

import { AUTH_EXPIRED_EVENT } from "@/lib/auth";

export default function SessionExpiredHandler() {
	const router = useRouter();
	const pathname = usePathname();
	const pathnameRef = useRef(pathname);

	useEffect(() => {
		pathnameRef.current = pathname;
	}, [pathname]);

	useEffect(() => {
		const onExpired = () => {
			toast.error("Your session expired. Please sign in again.");
			const current = pathnameRef.current ?? "/";
			if (current.startsWith("/signin") || current.startsWith("/signup")) {
				return;
			}
			router.replace("/signin");
		};

		window.addEventListener(AUTH_EXPIRED_EVENT, onExpired);
		return () => window.removeEventListener(AUTH_EXPIRED_EVENT, onExpired);
	}, [router]);

	return null;
}
