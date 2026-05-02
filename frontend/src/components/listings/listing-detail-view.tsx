import Image from "next/image";
import Link from "next/link";
import {
	ArrowLeft,
	BadgeCheck,
	Bath,
	Bed,
	Calendar,
	Check,
	Heart,
	Share2,
	Star,
	Wifi,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
	type ListingWithDetail,
	estimatedLeaseMonths,
	formatListingCurrency,
	formatListingLongDate,
	listingHeroSrc,
} from "@/lib/listings";

interface ListingDetailViewProps {
	readonly listing: ListingWithDetail;
}

export function ListingDetailView({ listing }: ListingDetailViewProps) {
	const months = estimatedLeaseMonths(listing.start_date, listing.end_date);
	const totalEstimate = listing.price * months;
	const hero = listingHeroSrc(listing);

	const bedrooms = listing.bedrooms ?? 1;
	const bathrooms = listing.bathrooms ?? 1;
	const wifi = listing.wifi_included ?? true;

	return (
		<main className="flex-1">
			<div className="border-b bg-background">
				<div className="mx-auto max-w-6xl px-4 py-3 md:px-6">
					<Link
						href="/"
						className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition hover:text-foreground"
					>
						<ArrowLeft className="size-4" aria-hidden />
						Back
					</Link>
				</div>
			</div>

			<div className="mx-auto max-w-6xl px-4 py-6 md:px-6 md:py-8">
				{hero ? (
					<div className="relative mb-8 overflow-hidden rounded-2xl ring-1 ring-foreground/10">
						<Image
							src={hero}
							alt={listing.title}
							width={1600}
							height={900}
							className="aspect-video w-full object-cover sm:aspect-21/9"
							priority
							sizes="(max-width: 768px) 100vw, min(1152px, 100vw)"
						/>
					</div>
				) : (
					<div className="mb-8 aspect-video w-full rounded-2xl bg-muted ring-1 ring-foreground/10 sm:aspect-21/9" />
				)}

				<div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
					<div className="min-w-0 space-y-2">
						<h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{listing.title}</h1>
						<div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
							<span>{listing.location}</span>
							{listing.rating != null && listing.review_count != null && (
								<>
									<span className="text-border">·</span>
									<span className="inline-flex items-center gap-1 text-foreground">
										<Star className="size-4 fill-foreground text-foreground" aria-hidden />
										<span className="font-medium">{listing.rating.toFixed(1)}</span>
										<span className="text-muted-foreground">
											({listing.review_count} reviews)
										</span>
									</span>
								</>
							)}
						</div>
						{listing.university ? (
							<p className="pt-1">
								<span className="inline-flex rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground">
									{listing.university}
								</span>
							</p>
						) : null}
					</div>
					<div className="flex shrink-0 gap-2 sm:pt-1">
						<Button type="button" variant="outline" size="icon" aria-label="Share listing">
							<Share2 />
						</Button>
						<Button type="button" variant="outline" size="icon" aria-label="Save listing">
							<Heart />
						</Button>
					</div>
				</div>

				<Card className="mb-10 flex flex-row items-center gap-4 px-5 py-5 sm:gap-5 sm:px-6">
					<div
						className="flex size-14 shrink-0 items-center justify-center rounded-full bg-muted text-base font-semibold text-foreground"
						aria-hidden
					>
						{listing.host_initials ?? "HS"}
					</div>
					<div className="min-w-0">
						<p className="flex flex-wrap items-center gap-2 font-medium">
							<span>Hosted by {listing.host_name ?? `Host #${listing.host_id}`}</span>
							{listing.host_verified ? (
								<span className="inline-flex items-center gap-0.5 text-sm font-normal text-blue-600 dark:text-blue-400">
									<BadgeCheck className="size-4 shrink-0" aria-hidden />
									Verified
								</span>
							) : null}
						</p>
						{listing.host_subtitle ? (
							<p className="text-sm text-muted-foreground">{listing.host_subtitle}</p>
						) : null}
					</div>
				</Card>

				<div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(280px,380px)] lg:items-start lg:gap-12">
					<div className="space-y-10">
						<section>
							<h2 className="mb-3 text-lg font-semibold">About this place</h2>
							<p className="text-muted-foreground leading-relaxed">{listing.description}</p>
							<ul className="mt-6 flex flex-wrap gap-6 text-sm">
								<li className="flex items-center gap-2">
									<Bed className="size-5 text-muted-foreground" aria-hidden />
									<span>
										{bedrooms} Bedroom{bedrooms !== 1 ? "s" : ""}
									</span>
								</li>
								<li className="flex items-center gap-2">
									<Bath className="size-5 text-muted-foreground" aria-hidden />
									<span>
										{bathrooms} Bathroom{bathrooms !== 1 ? "s" : ""}
									</span>
								</li>
								<li className="flex items-center gap-2">
									<Wifi className="size-5 text-muted-foreground" aria-hidden />
									<span>{wifi ? "WiFi included" : "WiFi"}</span>
								</li>
							</ul>
						</section>

						{listing.amenities && listing.amenities.length > 0 ? (
							<section>
								<h2 className="mb-4 text-lg font-semibold">Amenities</h2>
								<ul className="grid gap-3 sm:grid-cols-2">
									{listing.amenities.map((item) => (
										<li key={item} className="flex items-center gap-2 text-sm">
											<Check
												className="size-5 shrink-0 text-green-600 dark:text-green-500"
												strokeWidth={2.5}
												aria-hidden
											/>
											{item}
										</li>
									))}
								</ul>
							</section>
						) : null}

						<section className="flex items-start gap-3">
							<Calendar className="mt-0.5 size-5 shrink-0 text-muted-foreground" aria-hidden />
							<div>
								<h2 className="mb-1 text-lg font-semibold">Availability</h2>
								<p className="text-muted-foreground">
									{formatListingLongDate(listing.start_date)} –{" "}
									{formatListingLongDate(listing.end_date)}
								</p>
							</div>
						</section>
					</div>

					<aside className="lg:sticky lg:top-24">
						<Card className="gap-0 overflow-hidden p-0 shadow-md ring-foreground/15">
							<div className="space-y-1 px-6 pt-6">
								<p className="text-2xl font-semibold">
									{formatListingCurrency(listing.price)}
									<span className="text-base font-normal text-muted-foreground"> / month</span>
								</p>
								<p className="text-sm text-muted-foreground">
									Estimated {months} month{months !== 1 ? "s" : ""} total:{" "}
									<span className="font-medium text-foreground">
										{formatListingCurrency(totalEstimate)}
									</span>
								</p>
							</div>

							<div className="space-y-4 px-6 pt-6">
								<div className="space-y-2">
									<Label htmlFor="move-in">Move in</Label>
									<Input
										id="move-in"
										readOnly
										value={formatListingLongDate(listing.start_date)}
										className="rounded-xl bg-muted/50"
									/>
								</div>
								<div className="space-y-2">
									<Label htmlFor="move-out">Move out</Label>
									<Input
										id="move-out"
										readOnly
										value={formatListingLongDate(listing.end_date)}
										className="rounded-xl bg-muted/50"
									/>
								</div>
								<Button
									type="button"
									className="h-11 w-full rounded-xl bg-foreground text-background hover:bg-foreground/90"
								>
									Contact Host
								</Button>
								<p className="text-center text-xs text-muted-foreground">You won&apos;t be charged yet.</p>
							</div>

							<Separator className="my-6" />

							<div className="space-y-3 px-6 pb-6 text-sm">
								<div className="flex justify-between gap-4">
									<span className="text-muted-foreground">
										{formatListingCurrency(listing.price)} × {months} month{months !== 1 ? "s" : ""}
									</span>
									<span>{formatListingCurrency(totalEstimate)}</span>
								</div>
								<Separator />
								<div className="flex justify-between gap-4 font-semibold">
									<span>Total</span>
									<span>{formatListingCurrency(totalEstimate)}</span>
								</div>
							</div>
						</Card>
					</aside>
				</div>
			</div>
		</main>
	);
}
